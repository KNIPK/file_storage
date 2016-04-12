from file_storage import app
from flask import render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import posixpath


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.context_processor
def my_utility_processor():
    def join_path(a, b):
        return posixpath.join(a, b)

    return dict(join_path = join_path)


@app.route('/files/')
@app.route('/files/<path:path>')
def files_list(path = ""):
    upload_folder = app.config['UPLOAD_FOLDER']
    cur_path = os.path.join(upload_folder, path)
    dirs = [d for d in os.listdir(cur_path) if os.path.isdir(os.path.join(cur_path, d))]
    files = [d for d in os.listdir(cur_path) if os.path.isfile(os.path.join(cur_path, d))]
    return render_template('files_zone/files.html', path = path, dirs = dirs, files = files)


@app.route('/download/<path:path>')
def download(path):
    upload_folder = app.config['UPLOAD_FOLDER']
    return send_from_directory(directory = upload_folder, filename = path)


@app.route('/upload', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('files_list'))
    return render_template('files_zone/upload_form.html')
