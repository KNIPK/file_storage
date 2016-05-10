from file_storage import app,db,lm
from flask import render_template, request, redirect, url_for,send_file,flash
from flask_login import login_required,current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os
import posixpath
import shutil
from ..config import UPLOAD_FOLDER,EXT_DIC
from ..models import File,User,Directory,Member
from..forms.file_zone import DirForm


#--------------------------------------
#____________FUNKCJE___________________

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

@login_required
@app.context_processor
def my_utility_processor():
    def give_current_username():
        return current_user.username
    return dict(give_current_username = give_current_username)

@login_required
@app.context_processor
def my_utility_processor():
    def is_dir_owner(directory_id):
        current_dir = Directory.query.filter_by(id=directory_id).first_or_404()
        if current_dir.owner_id == current_user.id:
            return True
    return dict(is_dir_owner = is_dir_owner)



@login_required
def route_dir_tree(user,directory):
    main_dir = os.path.join(UPLOAD_FOLDER,current_user.username)
    route = []
    owner = User.query.filter_by(username=user).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    while actual_dir.holder_id:
        route.append(actual_dir.name)
        actual_dir = owner.directories.filter_by(id=actual_dir.holder_id).first_or_404()
    for x in reversed(route):
       main_dir = os.path.join(main_dir,x)
    return main_dir

@login_required
def route_dir_tree_download(user,directory):
    owner = User.query.filter_by(username=user).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    main_dir = os.path.join("upload_storage", owner.username)
    route = []
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

# @login_required
# def route_dir_tree_security(user,directory):
#     owner = User.query.filter_by(username=user).fisrt_or_404()
#     dir_to_check = owner.directories.filter_by(name=directory).first_or_404()
#
#     back_dir = owner.directories.filter_by(holder_id=dir_to_check.id).first()
#     while(back_dir != None):
#         if not check_for_access(back_dir.id):
#             flash("Nie masz dostepy do tego katalogu i/lub jego poprzednich katalogow")
#             return redirect(url_for('home'))
#         back_dir = owner.directories.filter_by(holder_id=back_dir.id).first()
#     return redirect(url_for('my_files',user=user,directory=directory))

@login_required
def check_for_access(directory_id):
    directory = Directory.query.filter_by(id=int(directory_id)).first()
    if not directory:
        return redirect(url_for('home'))
    if directory.owner_id == current_user.id:
        return True
    if directory.access:
        return True
    for record in directory.white_list.all():
        if record.member_id == current_user.id:
            return True
    return False

#-----------Access Required Decorator--------------------
def access_required(func):
    @wraps(func)
    def decorated_view(user,directory,*args, **kwargs):
        dir_owner = User.query.filter_by(username=user).first_or_404()
        dir_to_check = dir_owner.directories.filter_by(name=directory).first_or_404()
        white_list = dir_to_check.white_list.all()

        #debuger
        print("Verified:")
        print(dir_to_check)
        #-----------------

        # ---------Access to previous directories-------------
        back_dir = dir_owner.directories.filter_by(id=dir_to_check.holder_id).first()
        if back_dir:
            while (back_dir.holder_id != None):
                if not check_for_access(back_dir.id):
                    print("Dont have access to Dir:",str(back_dir.name))
                    flash("Nie masz dostepy do tego katalogu i/lub jego poprzednich katalogow")
                    return redirect(url_for('home'))
                back_dir = dir_owner.directories.filter_by(id=back_dir.holder_id).first()

        #---------Access for owner---------------------------
        if dir_to_check.owner_id == current_user.id:
            print("User is an owner")
            return func(user, directory, *args, **kwargs)

        #---------Access needed overall----------------------
        if dir_to_check.access:
            print("Access allowed for all")
            return func(user,directory,*args, **kwargs)

        # --------Access to request directory-----------------
        for record in white_list:
            if current_user.id == record.member_id:
                print("Access allowed for: ",str(current_user.username))
                return func(user, directory, *args, **kwargs)

        #-------------Password request-----------------------
        print("Access denied")
        return redirect(url_for('dir_whitelist',user = user, directory=directory))

    return decorated_view






#---------------------------
#---------ROUTES------------

@app.route('/makedir/<directory>',methods=['POST','GET'])
@login_required
def makedir(directory):
    form = DirForm()
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    if not owner.directories.filter_by(name=directory).first_or_404():
        pass
    if form.validate_on_submit():



        user_dirs = owner.directories.all()
        for x in user_dirs:
            if request.form['dirname'] == x.name:
                flash("Istnieje juz katalog o takie nazwie")
                print("Podaj inna nazwe katalogu")
                return render_template('files_zone/new_dir.html', form=form)

        actual_dir = owner.directories.filter_by(name=directory).first_or_404()
        actual_dir_id = actual_dir.id

        make = Directory(request.form['dirname'],current_user.id,actual_dir_id)
        secured = 'secure' in request.form
        if secured:
            make.deny(request.form['password'])

        try:

            dir_path = os.path.join(route_dir_tree(owner.username,directory),request.form['dirname'])
            os.mkdir(dir_path)
            db.session.add(make)
            db.session.commit()
        except:
            print("Nie udalo sie utworzyc")
            return render_template('files_zone/new_dir.html', form=form)

        if secured:
            dir_security = Member(make.id,current_user.id)
            try:
                db.session.add(dir_security)
                db.session.commit()
            except:
                print("Nie udalo sie zabezpieczyc katalogu")
                return render_template('files_zone/new_dir.html', form=form)

        return redirect(url_for('my_files',user = owner.username,directory=actual_dir.name))
    return render_template('files_zone/new_dir.html',form=form)




@app.route('/deletedirectory/<directory_id>')
@login_required
def delete_directory(directory_id):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    dir_to_delete = Directory.query.filter_by(id=int(directory_id)).first_or_404()
    if not dir_to_delete.owner_id == current_user.id:
        print("Nie mozesz usunac katalogu, innego uzytkownika")
        return redirect(url_for('home'))
    back_ref = None
    if dir_to_delete.holder_id:
        back_ref = owner.directories.filter_by(id=dir_to_delete.holder_id).first().name
    dir_path = route_dir_tree(owner.username,dir_to_delete.name)
    try:
        shutil.rmtree(dir_path)
        db.session.delete(dir_to_delete)
        for dir in route_back_ref_tree():
            db.session.delete(dir)
        db.session.commit()
        for member in Member.query.filter_by(directory=None).all():
            db.session.delete(member)
        db.session.commit()

    except:
        flash("Wystapil nieznany blad, Nie mozna bylo usunac pliku")
        return  redirect(url_for('my_files',user = owner.username,directory=dir_to_delete.name))
    return redirect(url_for('my_files',user = owner.username,directory=back_ref))


@app.route('/deletefile/<directory>/<file>')
@login_required
def delete_item(directory,file):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    dir_path = owner.directories.filter_by(name=directory).first_or_404()
    file_to_delete = dir_path.files.filter_by(name=file).first()
    file_path = os.path.join(route_dir_tree(owner.username,directory),file_to_delete.name)

    try:
        os.remove(file_path)
        db.session.delete(file_to_delete)
        db.session.commit()
    except:
        flash("Wystapil nieznany blad, Nie mozna bylo usunac pliku")
    return redirect(url_for('my_files',user = owner.username,directory=dir_path.name))





@app.route('/accessdenied/<user>/<directory>',methods=['POST','GET'])
@login_required
def dir_whitelist(user,directory):
    if current_user.is_authenticated:
        owner = User.query.filter_by(username=str(user)).first_or_404()
        actual_dir = owner.directories.filter_by(name=directory).first_or_404()
        back_dir = None
        if actual_dir.holder_id:
            back_dir = owner.directories.filter_by(id=actual_dir.holder_id).first().name
        if request.method == 'POST':
            print("Checking password....")
            pass_to_check = request.form['dir_pass']

            if actual_dir.check_password(pass_to_check):
                print("Password correct")
                new_member = Member(actual_dir.id, current_user.id)
                try:
                    db.session.add(new_member)
                    db.session.commit()
                except:
                    flash("Nie mozna było zapisac, sprobuj ponownie pozniej")
                    return render_template('files_zone/dir_password.html', dirname=actual_dir.name,user = owner.username,back_dir=back_dir)
                return redirect(url_for('my_files',user = user,directory=actual_dir.name))
            print("Incorrect")
        return render_template('files_zone/dir_password.html',dirname=actual_dir.name,user = owner.username,back_dir=back_dir)



@app.route('/files/<user>/<directory>')
@access_required
@login_required
def my_files(user,directory):
    if current_user.is_authenticated:
        dir_owner = User.query.filter_by(username=user).first_or_404()
        actual_dir = dir_owner.directories.filter_by(name=directory).first_or_404()
        actual_dir_id = actual_dir.id
        back_dir = None
        if actual_dir.holder_id:
            back_dir = dir_owner.directories.filter_by(id=actual_dir.holder_id).first().name
        dir_list = dir_owner.directories.filter_by(holder_id=actual_dir_id).all()
        file_list = actual_dir.files.all()
        return render_template('files_zone/files.html', dirs=dir_list, files=file_list,current_dir=actual_dir,back_dir=back_dir,user=dir_owner.username)
    return redirect('/home')


@app.route('/download/<user>/<directory>/<file>')
@access_required
@login_required
def download(user,directory,file):
    owner = User.query.filter_by(username=user).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    file_to_dl = actual_dir.files.filter_by(name=file).first_or_404()

    dir_path = route_dir_tree_download(owner.username,directory)
    file_path = os.path.join(dir_path,file_to_dl.name)
    return send_file(file_path,as_attachment=True)


@app.route('/upload/<directory>', methods = ['GET', 'POST'])
@login_required
def upload_file(directory):
    owner = User.query.filter_by(username=str(current_user.username)).first_or_404()
    actual_dir = owner.directories.filter_by(name=directory).first_or_404()
    if request.method == 'POST':
        dir_path = route_dir_tree(owner.username,directory)

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
            return redirect(url_for('my_files',user = owner.username,directory=actual_dir.name))
    return render_template('files_zone/upload_form.html',current_dir=actual_dir.name)



@app.route('/friends')
@login_required
def friends_list():
    friends = User.query.all()
    return render_template('files_zone/shared_files.html',friends=friends)

