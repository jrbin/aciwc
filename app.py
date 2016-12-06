import functools
import math
import os
import random
import string
import hashlib
from datetime import date, timedelta

import requests
from apscheduler.schedulers.gevent import GeventScheduler
from bs4 import BeautifulSoup
from dateutil.parser import parse
from flask import Flask, send_from_directory, render_template, request, \
    redirect, url_for, session, Response
from sqlalchemy import extract
from sqlalchemy.orm import joinedload, contains_eager
from werkzeug.utils import secure_filename

from db import *
from pgdb import Session, Person, Organization

with open("config.yml", 'r') as config_file:
    cfg = yaml.load(config_file)

ACCESS_RECORD = dict()
ACCESS_THRESHOLD = 5
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
CWD = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(CWD, 'static', 'img')

# app = Flask(__name__, static_url_path='', template_folder='')
app = Flask(__name__)
app.secret_key = cfg['flask']['session_key']

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_TEMPLATE = os.path.join(APP_ROOT, 'templates')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return (username == cfg['admin']['username']
            and password == cfg['admin']['password'])


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


@app.route('/')
def root():
    partners = select_partner_all()
    introduction = None
    for item in partners:
        if item.id == 1:
            introduction = item
    partners = [item for item in partners if item.id != 1]
    heroes = select_hero_all()
    links = select_link_all()
    return render_template('index.html', partners=partners, heroes=heroes,
                           introduction=introduction, links=links)


@app.route('/<folder>/<path:path>')
def send_img(folder, path):
    return send_from_directory('static/' + folder, path)


@app.route("/activity/")
@app.route("/activity/<int:activity_id>")
def activity(activity_id=None):
    if activity_id is None:
        now = datetime.now()
        activities = select_activity_all()
        old_activities = [item for item in activities
                          if item.activity_time < now]
        activities = [item for item in activities if item.activity_time >= now]
        links = select_link_all()
        return render_template('activity.html',
                               activities=activities,
                               old_activities=old_activities,
                               links=links)

    act = select_activity_by_id(activity_id)
    return render_template('activity_detail.html', activity=act)


@app.route("/manage/", methods=["GET", "POST"])
@app.route("/manage/<entity>", methods=["GET", "POST"])
@requires_auth
def manage(entity='partner'):
    if request.method == "GET":
        items = None
        if entity == 'hero':
            items = select_hero_all()
        if entity == 'partner':
            items = select_partner_all(hidden=None)
        if entity == 'activity':
            items = select_activity_all(hidden=None)
        if entity == 'link':
            items = select_link_all()
        if entity == 'email':
            items = get_misc('email')
        return render_template('manage.html', entity=entity, items=items)

    if entity == 'hero':
        image_url = request.form['image_url']
        description = request.form['description']
        insert_hero(image_url, description)
    elif entity == 'link':
        name = request.form['name']
        url = request.form['url']
        insert_link(name, url)
    elif entity == 'email':
        email = request.form['email']
        set_misc('email', email)
    else:
        return '', 400

    return redirect(url_for('manage', entity=entity))


@app.route("/edit/<entity>/", methods=["GET", "POST"])
@app.route("/edit/<entity>/<int:entity_id>", methods=["GET", "POST"])
@requires_auth
def edit(entity: str, entity_id: int = None):
    if request.method == "GET":
        item = None
        if entity_id is not None:
            if entity == 'partner':
                item = select_partner_by_id(entity_id)
            if entity == 'activity':
                item = select_activity_by_id(entity_id)
        return render_template('edit.html', entity=entity, item=item)

    # request.method == "POST"

    if entity == 'partner':
        logo_url = request.form['logo_url']
        html = request.form['html']

        if entity_id is None:
            insert_partner(logo_url, html)
        else:
            update_partner(entity_id,
                           dict(logo_url=logo_url, html=html))

    if entity == 'activity':
        title = request.form['title']
        html = request.form['html']
        activity_time = parse(request.form['activity_time'])
        soup = BeautifulSoup(html)
        thumbnail = soup.find('img')
        if thumbnail is not None:
            thumbnail = thumbnail['src']

        if entity_id is None:
            insert_activity(title, html, thumbnail, activity_time)
        else:
            update_activity(entity_id,
                            dict(title=title, html=html, thumbnail=thumbnail,
                                 activity_time=activity_time))

    return redirect(url_for('manage', entity=entity))


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
@requires_auth
def upload():
    # check if the post request has the file part
    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return 'No selected file', 400
    filename_root, ext = os.path.splitext(file.filename)
    if ext.lower() in ALLOWED_EXTENSIONS:
        hash = hashlib.sha224(file.read()).hexdigest()[:16]
        filename = secure_filename(filename_root + '.' + hash + ext)
        file.seek(0)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return url_for('send_img', folder='img', path=filename)
    return 'file extension not allowed', 400


@app.route("/toggle/<entity>/<int:entity_id>")
@requires_auth
def hide(entity: str, entity_id: int):
    if entity == 'partner':
        toggle_partner(entity_id)
    if entity == 'activity':
        toggle_activity(entity_id)
    return redirect(url_for('manage', entity=entity))


@app.route("/remove/<entity>/<int:entity_id>")
@requires_auth
def remove(entity: str, entity_id: int):
    if entity == 'partner':
        remove_partner(entity_id)
    if entity == 'activity':
        remove_activity(entity_id)
    if entity == 'hero':
        remove_hero(entity_id)
    if entity == 'link':
        remove_link(entity_id)
    return redirect(url_for('manage', entity=entity))


@app.route("/contact")
def contact():
    links = select_link_all()
    return render_template('contact.html', links=links)


def send_email(to: list or tuple, subject: str, content: str, fr=cfg['mailgun']['default_smtp_login'], html=False):
    if html:
        data = {"from": fr, "to": to, "subject": subject, "html": content}
    else:
        data = {"from": fr, "to": to, "subject": subject, "text": content}
    return requests.post(
        cfg['mailgun']['api_url'],
        auth=("api", cfg['mailgun']['api_key']),
        data=data)


def check_ip_frequency(ip):
    access_list = ACCESS_RECORD.get(ip, [])
    access_list.sort()
    now = datetime.now()
    hour_ago = now - timedelta(hours=1)
    access_list = [access_time for access_time in access_list
                   if access_time >= hour_ago]
    if len(access_list) >= ACCESS_THRESHOLD:
        ACCESS_RECORD[ip] = access_list
        return False

    access_list.append(now)
    ACCESS_RECORD[ip] = access_list
    return True


@app.route("/send", methods=["POST"])
def send():
    sliptcha_token = request.form['sliptcha_token']
    session_token = session.get('sliptcha_token')
    if session_token and sliptcha_token == session_token:
        session.pop('sliptcha_token', None)
    else:
        return '验证码错误', 400

    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    if not check_ip_frequency(client_ip):
        return '访问过于频繁', 400

    email = request.form["email"].strip()
    content = request.form["content"].strip()
    phone = request.form["phone"].strip()
    organization = request.form['organization'].strip()
    content += '\n\n------\nemail: ' + email
    if phone:
        content += '\n电话: ' + phone
    if organization:
        content += '\n公司: ' + organization
    to = (get_misc('email'),)
    r = send_email(to, '网站反馈', content, email)
    if r.status_code >= 400:
        return r.text, r.status_code
    return r.text


def random_string(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


@app.route("/sliptcha", methods=["POST"])
def sliptcha():
    positions = request.json
    if len(positions) < 10:
        return ""

    threshold = 20
    if len(positions) >= 2 * threshold:
        step = len(positions) // threshold
        positions = [positions[i * step] for i in range(threshold)]

    diffs = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
    mean = sum(diffs) / len(diffs)
    deviation = math.sqrt(
        sum([math.pow(mean - diff, 2) for diff in diffs])
        / (len(diffs) - 1)
    )

    if deviation <= 2:
        return ""

    sliptcha_token = random_string()
    session['sliptcha_token'] = sliptcha_token
    return sliptcha_token


def get_or_create(db_session, model, **kwargs):
    instance = db_session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        db_session.add(instance)
        return instance


@app.route('/person', methods=['GET', 'POST'])
@requires_auth
def person():
    db = Session()
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        phone = request.form['phone'].strip()
        organization = request.form['organization'].strip()
        organization = get_or_create(db, Organization, name=organization)
        position = request.form['position'].strip()
        extra = request.form['extra'].strip()
        birthday = request.form['birthday'].strip() or None
        if 'sendingEmail' in request.form:
            sending_email = True
        else:
            sending_email = False
        person_obj = Person(
            name=name, email=email, phone=phone, position=position, extra=extra, birthday=birthday,
            organization=organization, sending_email=sending_email)
        db.add(person_obj)
        db.commit()
        return redirect(url_for('person', action='add'))

    # GET
    action = request.args.get('action', 'list')
    if action == 'list' or action == 'download':
        name = request.args.get('name')
        email = request.args.get('email')
        organization = request.args.get('organization')
        date_from = request.args.get('dateFrom')
        date_to = request.args.get('dateTo')
        person_id = request.args.get('id')
        phone = request.args.get('phone')
        position = request.args.get('position')
        extra = request.args.get('extra')

        page = int(request.args.get('page', 1))
        num = int(request.args.get('num', 10))

        query = db.query(Person).join(Person.organization).options(contains_eager(Person.organization))
        if name:
            query = query.filter(Person.name.ilike('%{}%'.format(name.strip())))
        if email:
            query = query.filter(Person.email.ilike('%{}%'.format(email.strip())))
        if organization:
            query = query.filter(Organization.name.ilike('%{}%'.format(organization.strip())))
        if date_from and date_to:
            query = query.filter(Person.birthday.between(date_from.strip(), date_to.strip()))
        if person_id:
            query = query.filter(Person.id == person_id.strip())
        if phone:
            query = query.filter(Person.phone.ilike('%{}%'.format(phone.strip())))
        if position:
            query = query.filter(Person.position.ilike('%{}%'.format(position.strip())))
        if extra:
            query = query.filter(Person.extra.ilike('%{}%'.format(extra.strip())))

        if action == 'download':
            def csv_generator():
                yield 'Name,Email,Phone,Organization,Position,Birthday,Extra\n'
                for p in query.all():
                    yield ','.join([p.name,
                                    p.email,
                                    p.phone,
                                    p.organization.name,
                                    p.position,
                                    p.birthday.strftime('%Y-%m-%d') if p.birthday else '',
                                    p.extra]) + '\n'
            return Response(csv_generator(),
                            mimetype='text/csv',
                            headers={'Content-Disposition': 'attachment;filename=data.csv'})

        count = query.count()
        total_pages = (count + num - 1) // num
        total_pages = max(1, total_pages)
        page = max(1, min(total_pages, page))
        pages = 10
        left = page - pages // 2
        right = page + (pages - 1) // 2
        if left < 1:
            left = 1
            right = min(total_pages, left + pages - 1)
        elif right > total_pages:
            right = total_pages
            left = max(1, right - pages + 1)
        offset = (page - 1) * num

        people = query.order_by(Person.id.desc()).limit(num).offset(offset).all()
        return render_template('person.html', people=people, page=page, num=num,
                               count=count, total_pages=total_pages, left=left,
                               right=right, action=action, name=name, email=email,
                               organization=organization, dateFrom=date_from, dateTo=date_to,
                               id=person_id, phone=phone, position=position, extra=extra)
    else:
        return render_template('person.html', action=action)


@app.route('/person/<int:person_id>', methods=['PUT', 'DELETE'])
@requires_auth
def person_single(person_id=None):
    db = Session()

    if request.method == 'PUT':
        person_obj = db.query(Person).filter(Person.id == person_id).first()
        data = None
        if 'name' in request.form:
            data = person_obj.name = request.form['name']
        if 'email' in request.form:
            data = person_obj.email = request.form['email']
        if 'organization' in request.form:
            person_obj.organization = get_or_create(db, Organization, name=request.form['organization'].strip())
            data = person_obj.organization.name
        if 'birthday' in request.form:
            data = person_obj.birthday = request.form['birthday']
        if 'sendingEmail' in request.form:
            data = person_obj.sending_email = request.form['sendingEmail']
        if 'phone' in request.form:
            data = person_obj.phone = request.form['phone']
        if 'position' in request.form:
            data = person_obj.position = request.form['position']
        if 'extra' in request.form:
            data = person_obj.extra = request.form['extra']
        db.commit()
        return data

    if request.method == 'DELETE':
        db.query(Person).filter(Person.id == person_id).delete(synchronize_session=False)
        db.commit()
        return ''


@app.route('/batch', methods=['POST'])
@requires_auth
def person_batch():
    file = request.files['file']
    target = request.form['target']
    action = request.form['action']

    db = Session()

    if target == 'person' and action == 'insert':
        col_dict = {
            'name': 0,
            'email': 1,
            'phone': 2,
            'organization': 3,
            'position': 4,
            'birthday': 5,
            'extra': 6,
        }
        people = []
        line = file.readline().strip().decode()
        values = line.split(',')
        if len(values) > 0 and values[0] in col_dict:
            for i, val in enumerate(values):
                val = val.strip().lower()
                col_dict[val] = i
        else:
            file.seek(0)

        for line in file.readlines():
            line = line.strip().decode()
            if not line:
                continue
            values = line.split(',')
            name = values[col_dict['name']].strip()
            email = values[col_dict['email']].strip()
            phone = values[col_dict['phone']].strip()
            organization = values[col_dict['organization']].strip()
            organization = get_or_create(db, Organization, name=organization)
            position = values[col_dict['position']].strip()
            birthday = values[col_dict['birthday']].strip()
            extra = values[col_dict['extra']].strip()
            person_obj = Person(
                name=name, email=email, phone=phone, birthday=birthday,
                organization=organization, position=position, sending_email=True, extra=extra)
            people.append(person_obj)
        db.add_all(people)
        db.commit()
        return redirect(url_for('person'))


def send_birthday_email():
    db = Session()
    with open(os.path.join(APP_TEMPLATE, 'birthday.html')) as f:
        html_content = f.read()
    today = date.today()
    people = db.query(Person) \
        .filter(Person.sending_email == True) \
        .filter(extract('month', Person.birthday) == today.month) \
        .filter(extract('day', Person.birthday) == today.day) \
        .all()
    print('sending birthday email to %d people' % len(people))
    for person_obj in people:
        send_email([person_obj.email],
                   '澳大利亚国际微商总会祝您生日快乐',
                   html_content.replace('${name}', person_obj.name),
                   html=True, fr=get_misc('email'))


scheduler = GeventScheduler()
scheduler.add_job(send_birthday_email, 'cron', hour=18, minute=30)
scheduler.start()

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1')
