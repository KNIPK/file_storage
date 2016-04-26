from file_storage import app,db,lm
from flask import render_template, request, redirect, url_for,send_file,flash
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import os
import posixpath
from ..config import UPLOAD_FOLDER,EXT_DIC
from ..models import File,User,Directory
from..forms.file_zone import DirForm


@lm.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()

@app.route('/')
def hello_world():
    return 'Hello World!'


@app.context_processor
def my_utility_processor():
    def join_path(a, b):
        return posixpath.join(a, b)

    return dict(join_path = join_path)


@app.context_processor
def my_utility_processor():
    def check_ext(file_ext):
        if file_ext in EXT_DIC:
            return 'fa fa-file-' + EXT_DIC[file_ext] + '-o fa-lg'
        return 'fa fa-file-o fa-lg'

    return dict(check_ext=check_ext)




# @app.route('/filesxx/')
# @app.route('/filesxx/<path:path>')
# @login_required
# def files_list(path = ""):
#     upload_folder = UPLOAD_FOLDER
#     cur_path = os.path.join(upload_folder, path)
#     dirs = [d for d in os.listdir(cur_path) if os.path.isdir(os.path.join(cur_path, d))]
#     files = [d for d in os.listdir(cur_path) if os.path.isfile(os.path.join(cur_path, d))]
#     return render_template('files_zone/files.html', path = path, dirs = dirs, files = files)


@app.route('/makedir',methods=['POST','GET'])
@login_required
def makedir():
    form = DirForm()
    if form.validate_on_submit():
        make = Directory(request.form['dirname'],current_user.id)
        try:
            user_path = os.path.join(UPLOAD_FOLDER,current_user.username)
            dir_path = os.path.join(user_path,request.form['dirname'])
            os.mkdir(dir_path)
            db.session.add(make)
            db.session.commit()
        except:
            print("Nie udalo sie utworzyc")
        return redirect(url_for('my_files'))
    return render_template('files_zone/new_dir.html',form=form)




@app.route('/delete/<int:dir>/<int:item_id>')
@login_required
def delete_item(dir,item_id):
    dir_path = os.path.join(UPLOAD_FOLDER,current_user.username)
    to_remove = None
    files = File.query.filter_by(directory_id=dir).all()
    for x in files:
        if x.id == item_id:
            to_remove = x
            break
    if to_remove != None:
        os.remove(os.path.join(dir_path, to_remove.name))
        db.session.delete(to_remove)
        db.session.commit()
    return redirect(url_for('my_files'))


@app.route('/files/')
@app.route('/files/<path:path>')
@login_required
def my_files(path=""):
    upload_folder = UPLOAD_FOLDER
    cur_path = os.path.join(upload_folder, path)
    if current_user.is_authenticated:
        owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
        dir_list = owner.directories.all()
        print(dir_list)
        file_list = dir_list[0].files.all()
        return render_template('files_zone/files.html',path=path,dirs=dir_list,files=file_list)
    return redirect('/home')


@app.route('/download/<path:path>')
@login_required
def download(path):
    dir_path = 'upload_storage/'+current_user.username
    file_path = os.path.join(dir_path,path)
    return send_file(file_path,as_attachment=True)



@app.route('/upload', methods = ['GET', 'POST'])
@login_required
def upload_file():
    user_path = os.path.join(UPLOAD_FOLDER,current_user.username)
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.is_authenticated:
            filename = secure_filename(file.filename)
            new_file = File(filename,directory_id=1)
            try:
                file.save(os.path.join(user_path, filename))
                db.session.add(new_file)
                db.session.commit()
                flash("Udalo sie ; )")
            except:
                flash("Nie udalo sie przeslac pliku")
            return redirect(url_for('files_list'))
    return render_template('files_zone/upload_form.html')
