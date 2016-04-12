from flask_mail import Message, Mail
from file_storage import app


def send_email(email, subject, html):
    mail = Mail(app)
    msg = Message(subject = subject, recipients = [email], html = html)
    mail.send(msg)
