"""Функция send_massage отправляет новые позиции на почту, обязательно заполните поля setting"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from setting import email_adres_from, email_paaword, email_adres_to
import smtplib


def send_massage(massage, topic_name):
    msg = MIMEMultipart()
    message = massage
    password = email_paaword
    msg['From'] = email_adres_from
    msg['To'] = email_adres_to
    msg['Subject'] = topic_name
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
