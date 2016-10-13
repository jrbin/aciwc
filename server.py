import os

from flask import Flask, send_from_directory, render_template, request, flash,\
    redirect, url_for
from werkzeug.utils import secure_filename
from bs4 import BeautifulSoup

from db import insert_activity, update_activity, select_activity_all,\
    insert_partner, update_partner, select_partner_all, select_partner_by_id,\
    select_activity_by_id, toggle_partner, toggle_activity, remove_activity, \
    remove_partner

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__, static_url_path='', template_folder='')
app.config['UPLOAD_FOLDER'] = 'img/'


@app.route('/')
def root():
    partners = select_partner_all()
    return render_template('index.html', partners=partners)


@app.route("/activity/")
@app.route("/activity/<int:activity_id>")
def activity(activity_id=None):
    if activity_id is None:
        activities = select_activity_all()
        return render_template('activity.html', activities=activities)

    act = select_activity_by_id(activity_id)
    return render_template('activity_detail.html', activity=act)


@app.route("/img/<path:path>")
def send_img(path):
    return send_from_directory('img', path)


@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory('css', path)


@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory('js', path)


@app.route("/manage/")
@app.route("/manage/<entity>")
def manage(entity='partner'):
    items = None
    if entity == 'partner':
        items = select_partner_all(hidden=None)
    if entity == 'activity':
        items = select_activity_all(hidden=None)
    return render_template('manage.html', entity=entity, items=items)


@app.route("/edit/<entity>/", methods=["GET", "POST"])
@app.route("/edit/<entity>/<int:entity_id>", methods=["GET", "POST"])
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
        soup = BeautifulSoup(html)
        thumbnail = soup.find('img')
        if thumbnail is not None:
            thumbnail = thumbnail['src']

        if entity_id is None:
            insert_activity(title, html, thumbnail)
        else:
            update_activity(entity_id,
                            dict(title=title, html=html, thumbnail=thumbnail))

    return redirect(url_for('manage', entity=entity))


def allowed_file(filename):
    return '.' in filename and \
           filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload():
    # check if the post request has the file part
    if 'image' not in request.files:
        return 'No file part', 400
    file = request.files['image']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        return 'No selected file', 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return url_for('send_img', path=filename)
    return 'file extension not allowed', 400


@app.route("/toggle/<entity>/<int:entity_id>")
def hide(entity: str, entity_id: int):
    if entity == 'partner':
        toggle_partner(entity_id)
    if entity == 'activity':
        toggle_activity(entity_id)
    return redirect(url_for('manage', entity=entity))


@app.route("/remove/<entity>/<int:entity_id>")
def remove(entity: str, entity_id: int):
    if entity == 'partner':
        remove_partner(entity_id)
    if entity == 'activity':
        remove_activity(entity_id)
    return redirect(url_for('manage', entity=entity))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
