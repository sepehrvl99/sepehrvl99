import smtplib
from email.mime.text import MIMEText
from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')

SMTP_SERVER = config['Email']['SmtpServer']
SMTP_PORT = config['Email'].getint('SmtpPort')
FROM_EMAIL = config['Email']['FromEmail']
TO_EMAIL = config['Email']['ToEmail']
USERNAME = config['Email']['Username']
PASSWORD = config['Email']['Password']

def send_email(subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(USERNAME, PASSWORD)
        server.send_message(msg)
