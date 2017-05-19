import functools
import hashlib
import math
import random
import smtplib
import ssl
import string
from datetime import timedelta
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
from flask import Flask, send_from_directory, render_template, request, \
    redirect, url_for, session, Response
from werkzeug.utils import secure_filename

from db import *

CWD = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(CWD, 'config.yml'), 'r') as config_file:
    cfg = yaml.load(config_file)

ACCESS_RECORD = dict()
ACCESS_THRESHOLD = 5
ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif'}
UPLOAD_FOLDER = os.path.join(CWD, 'static', 'img')

# app = Flask(__name__, static_url_path='', template_folder='')
app = Flask(__name__)
app.secret_key = cfg['flask']['session_key']

APP_TEMPLATE = os.path.join(CWD, 'templates')


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
        hashed = hashlib.sha224(file.read()).hexdigest()[:16]
        filename = secure_filename(filename_root + '.' + hashed + ext)
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


def send_email(fr: str, to: str, subject: str, txt='', html='', provider='smtp'):
    if provider == 'smtp':
        msg = MIMEMultipart('alternative')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = cfg['smtp']['login']
        msg['To'] = to

        part1 = MIMEText(txt.encode('utf-8'), 'plain', 'utf-8')
        msg.attach(part1)

        if html:
            part2 = MIMEText(html.encode('utf-8'), 'html', 'utf-8')
            msg.attach(part2)

        smtp_server = smtplib.SMTP('smtp.office365.com', port=587)
        ssl_context = ssl.create_default_context()
        smtp_server.starttls(context=ssl_context)
        smtp_server.login(cfg['smtp']['login'], cfg['smtp']['password'])
        smtp_server.send_message(msg)
        smtp_server.quit()

    else:
        r = requests.post(
            cfg['mailgun']['api_url'],
            auth=('api', cfg['mailgun']['api_key']),
            data={
                'from': fr or cfg['default_sender'],
                'to': to,
                'subject': subject,
                'text': txt,
                'html': html
            }
        )
        print(r.text)


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
    to = get_misc('email')
    try:
        send_email(email, to, '网站反馈', txt=content, provider='mailgun')
    except Exception as e:
        print(e)
        return '', 400
    return ''


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


@app.route('/ip')
def test_ip():
    return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)


@app.route('/newhome')
def new_home():
    return render_template('index2.html')


@app.route('/report')
def report():
    return render_template('report.html')


if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1')
