import smtplib
from email.mime.text import MIMEText
from config.celery_settings import celery_settings
from stllrent_bootstrap.exc import ImproperlyConfigured

def send_mail(body:str, subject: str, mail_to: str, mail_from: str):

    if not celery_settings.NOTIFICATION_EMAIL_RELAY:
        raise ImproperlyConfigured("E-MAIL NOTIFICATION requires NOTIFICATION_EMAIL_RELAY variable")

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = mail_from
    msg['To'] = mail_to

    server = smtplib.SMTP(celery_settings.NOTIFICATION_EMAIL_RELAY)
    if celery_settings.NOTIFICATION_EMAIL_STARTTLS:
        server.starttls() # Ativar TLS
    server.sendmail(from_addr=mail_from, to_addrs=mail_to, msg=msg.as_string())
    server.close()