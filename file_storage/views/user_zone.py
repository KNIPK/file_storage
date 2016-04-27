from flask import render_template, url_for, request, redirect, flash, abort
from flask_login import logout_user, login_user, login_required, current_user
from file_storage import app, db, lm
from ..forms.user_zone import RegisterForm, LoginForm, ChangeEmailForm, ChangePasswordForm, ResetPasswordForm
from ..models import User
from ..util.utils import send_email
from ..util.security import ts
from ..config import MAIL_DEFAULT_SENDER, SALT_CONFIRM_EMAIL, SALT_RESET_PASSWORD, UPLOAD_FOLDER
import os

add = "user_zone/"


@lm.user_loader
def load_user(user_id):
    return User.query.filter(id = user_id).first()


@app.route('/')
@app.route('/index')
def index():
    return render_template(add + 'index.html')


@app.route('/signup', methods = ['POST', 'GET'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        form = RegisterForm()
        if form.validate_on_submit():
            new_user = User(request.form['username'], request.form['password'], request.form['email'])
            if User.query.filter_by(email = new_user.email).first():
                flash("Taki email już istnieje")
                return redirect(url_for('signup'))
            if User.query.filter_by(username = new_user.username).first():
                flash("Taka nazwa użytkownika już istnieje")
                return redirect(url_for('signup'))

            db.session.add(new_user)
            db.session.commit()
            token = ts.dumps(new_user.email, salt = SALT_CONFIRM_EMAIL)

            confirm_url = url_for('confirm_email', token = token, _external = True)
            html = render_template(add + 'email_activate.html', confirm_url = confirm_url)
            send_email(new_user.email, 'Potwierdź swoje konto', html)
            flash("Konto zostało utworzone. Potwierdź je klikają w link aktywacyjny wysłany na podany adres email")
            return redirect(url_for('signup'))

        return render_template(add + 'signup.html', form = form, title = 'Rejestracja')


@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    elif "resend_activation_email" in request.form:
        user = User.query.filter_by(username = request.form['username']).first()
        token = ts.dumps(user.email, salt = SALT_CONFIRM_EMAIL)

        confirm_url = url_for('confirm_email', token = token, _external = True)
        html = render_template(add + 'email_new_email.html', confirm_url = confirm_url)
        send_email(user.email, 'Potwierdź swój email', html)
        flash("Email aktywacyjny został wysłany ponownie")
        return redirect(url_for('signin'))
    else:
        form = LoginForm()
        url_reset_password = url_for('reset_password')
        if form.validate_on_submit():
            name = User.query.filter_by(username = str(request.form['username'])).first()
            if name.check_password(request.form['password']):
                if not name.email_confirmed:
                    flash("Konto nie zostało aktywowane")
                    return render_template(add + 'signin.html', form = form, url_reset_password = url_reset_password,
                                           esend_activation_email = True)
                login_user(name)
                return redirect(url_for('home'))
            else:
                flash("Błędny login lub hasło")
        return render_template(add + 'signin.html', form = form, url_reset_password = url_reset_password,
                               resend_activation_email = False)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/home')
@login_required
def home():
    return render_template(add + 'home.html')


@app.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    pass_form, email_form = ChangePasswordForm(), ChangeEmailForm()
    user = current_user
    if 'submit_pass' in request.form and pass_form.validate_on_submit():
        old_password = request.form['old_password']
        password = request.form['password']
        if not user.check_password(old_password):
            flash("Twoje stare hasło się nie zgadza", "password")
            return redirect(url_for('account'))

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash("Hasło zostało poprawnie zmienione", "password")
        return redirect(url_for('account'))
    elif 'submit_email' in request.form and email_form.validate_on_submit():
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email = str(email)).first():
            flash("Taki email już istnieje", "email")
            return redirect(url_for('account'))
        if not user.check_password(password):
            flash("Podałeś złe hasło", "email")
            return redirect(url_for('account'))
        user.email = email
        user.email_confirmed = 0

        db.session.add(user)
        db.session.commit()

        token = ts.dumps(email, salt = SALT_CONFIRM_EMAIL)

        confirm_url = url_for('confirm_email', token = token, _external = True)
        html = render_template(add + 'email_new_email.html', confirm_url = confirm_url)
        send_email(user.email, 'Potwierdź swój email', html)
        flash("Email został zmieniony poprawnie. Link aktywacyjny został przesłany na twój nowy adres", "email")
        return redirect(url_for('account'))

    return render_template(add + 'account.html', pass_form = pass_form, email_form = email_form,
                           login = current_user.username, email = current_user.email)


@app.route('/help', methods = ['POST', 'GET'])
def help():
    if request.method == 'POST':
        email = request.form['help-email']
        subject = request.form['help-subject']
        description = request.form['help-description']
        html = render_template(add + 'email_help.html', email = email, description = description)
        send_email(MAIL_DEFAULT_SENDER, subject, html)
        flash("Wiadomość została wysłana poprawnie")
        return redirect(url_for('help'))
    return render_template(add + 'help.html')


@app.route('/confirm/<token>')
def confirm_email(token):
    email = None
    try:
        email = ts.loads(token, salt = SALT_CONFIRM_EMAIL, max_age = 86400)  # 24h
    except:
        abort(404)

    user = User.query.filter_by(email = email).first_or_404()
    if user.email_confirmed:
        abort(404)

    dir_path = os.path.join(UPLOAD_FOLDER, user.username)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    user.activate_user()
    db.session.add(user)
    db.session.commit()

    return redirect(url_for('signin'))


@app.route('/reset_password', methods = ['POST', 'GET'])
def reset_password():
    form = RegisterForm()
    if request.method == 'POST':
        user = User.query.filter_by(email = request.form['email']).first()
        if user is None:
            flash('Nie ma takiego użytkownika w bazie!', 'error')
        else:
            flash('Poprawny. Sprawdź pocztę', 'success')
            token = ts.dumps(user.email, salt = SALT_RESET_PASSWORD)
            recover_url = url_for('reset_with_token', token = token, _external = True)

            html = render_template(add + 'email_reset_password.html', recover_url = recover_url)

            send_email(user.email, 'Resetowanie hasła', html)

    return render_template(add + 'reset_password.html', form = form)


@app.route('/reset_password/<token>', methods = ["GET", "POST"])
def reset_with_token(token):
    email = None
    try:
        email = ts.loads(token, salt = SALT_RESET_PASSWORD, max_age = 86400)
    except:
        abort(404)

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email = email).first_or_404()
        user.set_password(request.form['password'])

        db.session.add(user)
        db.session.commit()
        flash("Hasło zostało poprawnie zmienione")
        return redirect(url_for('signin'))

    return render_template(add + 'new_password.html', form = form)
