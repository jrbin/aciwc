from flask import Flask, send_from_directory, render_template
import sys

app = Flask(__name__, static_url_path='', template_folder='')

@app.route('/')
@app.route('/<path>')
def root(path=''):
    if path == '':
        path = 'index.html'
    return render_template(path)

@app.route("/img/<path:path>")
def send_img(path):
    return send_from_directory('img', path)

@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory('css', path)

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory('js', path)

if __name__ == "__main__":
    app.run(debug=True)
