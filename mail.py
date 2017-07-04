#!/usr/bin/python
# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from config import *

def sendmail(receiver, receiver_name, subject, content, content_type = "plain"):
    print(" ==>> mail.py in vatic-admin")
    message = MIMEText(content, content_type, smtp_encoding)
    message['From'] = formataddr((str(Header(smtp_sender_name, smtp_encoding)) ,smtp_sender))
    message['To']   = formataddr((str(Header(receiver_name, smtp_encoding)) ,receiver))
    message['Subject'] = Header(subject, 'utf-8')

    try:
        smtpObj = smtplib.SMTP()

        smtpObj =smtplib.SMTP_SSL('smtp.gmail.com', 465)
        #smtpObj.connect(smtp_host, smtp_port)

        smtpObj.ehlo()
        #smtpObj.starttls()

        smtpObj.login(smtp_user,smtp_pass)
        smtpObj.sendmail(smtp_sender, receiver, message.as_string())
        print("成功寄信")
        return True
    except smtplib.SMTPException as error:
        print(error)
        return False



def call():
    from sys import argv
    try:
        mail = argv[1]
    except:
        print("using " + argv[0] + " <your@email.adress>");
        return -1

    receivers = mail
    receiver_name = "User"
    subject = 'Python SMTP Test'


    content = "Hello world!"
    content_type = 'plain'
    send = sendmail(receivers, receiver_name, subject, content, content_type)
    if send:
        print("send success")
        return 0
    else:
        print("sned fail, uncomment \"print(error)\" for detail")
        return 10

if __name__ == "__main__":
    from sys import exit
    exit(call())
