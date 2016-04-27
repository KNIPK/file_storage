from file_storage import app,db,lm
from flask import render_template, request, redirect, url_for,send_file,flash
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
import os
import posixpath
import shutil
from ..config import UPLOAD_FOLDER,EXT_DIC
from ..models import File,User,Directory
from..forms.file_zone import DirForm


@lm.user_loader
def load_user(user_id):
    return User.query.filter(User.id == int(user_id)).first()


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


@app.context_processor
@login_required
def my_utility_processor():
    def give_current_username():
        return current_user.username
    return dict(give_current_username = give_current_username)



@login_required
def route_dir_tree(directory):
    main_dir = os.path.join(UPLOAD_FOLDER,current_user.username)
    route = []
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    while actual_dir.holder_id:
        route.append(actual_dir.name)
        actual_dir = owner.directories.filter_by(id=actual_dir.holder_id).first_or_404()
    for x in reversed(route):
       main_dir = os.path.join(main_dir,x)
    return main_dir

@login_required
def route_dir_tree_download(directory):
    main_dir = os.path.join("upload_storage",current_user.username)
    route = []
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    while actual_dir.holder_id:
        route.append(actual_dir.name)
        actual_dir = owner.directories.filter_by(id=actual_dir.holder_id).first_or_404()
    for x in reversed(route):
       main_dir = os.path.join(main_dir,x)
    return main_dir

@login_required
def route_back_ref_tree():
    dirs_to_clear = []
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    dirs_to_check = owner.directories.all()

    for dir in dirs_to_check:
        if not owner.directories.filter_by(id=dir.holder_id).all() and not dir.hidden:
            dirs_to_clear.append(dir)

    return dirs_to_clear






@app.route('/makedir/<directory>',methods=['POST','GET'])
@login_required
def makedir(directory):

    form = DirForm()
    if form.validate_on_submit():
        owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
        actual_dir = owner.directories.filter_by(name=directory).first_or_404()

        actual_dir_id = actual_dir.id
        make = Directory(request.form['dirname'],current_user.id,actual_dir_id)

        try:

            dir_path = os.path.join(route_dir_tree(directory),request.form['dirname'])
            os.mkdir(dir_path)
            db.session.add(make)
            db.session.commit()
        except:
            print("Nie udalo sie utworzyc")
        return redirect(url_for('my_files',directory=actual_dir.name))
    return render_template('files_zone/new_dir.html',form=form)




@app.route('/deletedirectory/<directory>')
@login_required
def delete_directory(directory):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    dir_to_delete = owner.directories.filter_by(name=directory).first_or_404()
    back_ref = None
    if dir_to_delete.holder_id:
        back_ref = owner.directories.filter_by(id=dir_to_delete.holder_id).first().name
    dir_path = route_dir_tree(directory)
    try:
        shutil.rmtree(dir_path)
        db.session.delete(dir_to_delete)
        for dir in route_back_ref_tree():
            db.session.delete(dir)
        db.session.commit()
    except:
        flash("Wystapil nieznany blad, Nie mozna bylo usunac pliku")
        return  redirect(url_for('my_files',directory=dir_to_delete.name))
    return redirect(url_for('my_files',directory=back_ref))


@app.route('/deletefile/<directory>/<file>')
@login_required
def delete_item(directory,file):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    dir_path = owner.directories.filter_by(name=directory).first_or_404()
    file_to_delete = dir_path.files.filter_by(name=file).first()
    file_path = os.path.join(route_dir_tree(directory),file_to_delete.name)

    try:
        os.remove(file_path)
        db.session.delete(file_to_delete)
        db.session.commit()
    except:
        flash("Wystapil nieznany blad, Nie mozna bylo usunac pliku")
    return redirect(url_for('my_files',directory=dir_path.name))






@app.route('/files/<directory>')
@login_required
def my_files(directory):
    if current_user.is_authenticated:
        owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
        actual_dir = owner.directories.filter_by(name=directory).first_or_404()
        actual_dir_id = actual_dir.id
        back_dir = None
        if actual_dir.holder_id:
            back_dir = owner.directories.filter_by(id=actual_dir.holder_id).first().name

        dir_list = owner.directories.filter_by(holder_id=actual_dir_id).all()
        file_list = actual_dir.files.all()
        return render_template('files_zone/files.html', dirs=dir_list, files=file_list,current_dir=actual_dir.name,back_dir=back_dir)
    return redirect('/home')


@app.route('/download/<directory>/<file>')
@login_required
def download(directory,file):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    file_to_dl = actual_dir.files.filter_by(name=file).first_or_404()

    dir_path = route_dir_tree_download(directory)
    file_path = os.path.join(dir_path,file_to_dl.name)
    return send_file(file_path,as_attachment=True)


@app.route('/upload/<directory>', methods = ['GET', 'POST'])
@login_required
def upload_file(directory):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    if request.method == 'POST':
        dir_path = route_dir_tree(directory)

        file = request.files['file']
        if file and current_user.is_authenticated:
            filename = secure_filename(file.filename)
            if not actual_dir.files.filter_by(name=filename).first():
                new_file = File(filename,directory_id=actual_dir.id)
            else:
                flash("Plik o podanej nazwie istnieje juz w tym katalogu")
                return render_template('files_zone/upload_form.html', current_dir=actual_dir.name)
            try:
                file.save(os.path.join(dir_path, filename))
                db.session.add(new_file)
                db.session.commit()
                flash("Udalo sie ; )")
            except:
                flash("Nie udalo sie przeslac pliku")
            return redirect(url_for('my_files',directory=actual_dir.name))
    return render_template('files_zone/upload_form.html',current_dir=actual_dir.name)
