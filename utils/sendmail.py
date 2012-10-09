#-*- coding:utf-8 -*-

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import os
 

_TO_UNICODE_TYPES = (unicode, type(None))
def to_unicode(value):
    if isinstance(value, _TO_UNICODE_TYPES):
        return value
    return value.decode("utf-8")

    
def send_mail(mail, server="localhost"):
 
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['From'] = mail['From']
    msg['To'] = COMMASPACE.join(mail['To'])
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = to_unicode(mail['Subject'])
    
    text = mail.get('Text')
    if text:
        msg.attach(MIMEText(text, 'plain', 'utf-8' ))

    html = mail.get('Html')
    if html:
        msg.attach(MIMEText(html, 'html', 'utf-8'))
 
    files = mail.get('Files')

    if files:
        for f in files:
            #file = {'filename':fn, 'data':data}
            part = MIMEBase('application', "octet-stream")
            part.set_payload(f['data'])
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                           % os.path.basename(f['filename']))
            msg.attach(part)
 
    smtp = smtplib.SMTP(server)
    smtp.sendmail(mail['From'], mail['To'], msg.as_string() )
    smtp.close()

if __name__ == "__main__":
    send_mail({
            'To':['Li Meng Jun <lmjubuntu@gmail.com>'],
            'From':'lupino <lupino@yopmail.com>',
            'Subject':'Saying hello',
            'Text': 'You are best'
        })
