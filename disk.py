import imaplib
import config
import email
import base64
from utils import send_mail
import os
import hashlib
import json

class Disk:
    def __init__(self):
        if config.SSL:
            self.mail = imaplib.IMAP4_SSL(config.IAMP_HOST)
        else:
            self.mail = imaplib.IMAP4(config.IAMP_HOST)

    def login(self):
        self.mail.login(config.IAMP_USER, config.IAMP_PASSWD)

    def list(self):
        result, data = self.mail.list()
        if result.lower() == 'ok':
            return data
        return None

    def select(self, mailbox):
        self.mail.select(mailbox)

    def uid(self, From):
        result, data = self.mail.uid('SEARCH', None, '(HEADER FROM "%s")'%From)
        if result.lower() == 'ok':
            return data[0].split()
        return None

    def fetch(self, uid):
        result, data = self.mail.uid('FETCH', uid, '(RFC822)')
        if result.lower() == 'ok':
            raw_mail = data[0][1]
            email_message = email.message_from_string(raw_mail)
            maintype = email_message.get_content_maintype()
            retval = {}
            retval['subject'] = email_message['Subject']
            b = retval['subject'].find('?b?') + 3
            if b > 5:
                coding = retval['subject'][2:b-3]
                subject = base64.decodestring(retval['subject'][b:-2])
                retval['subject'] = subject.decode(coding)

            if maintype == 'multipart':
                for part in email_message.get_payload():
                    maintype = part.get_content_maintype()
                    payload = base64.decodestring(part.get_payload())
                    if maintype == 'text':
                        retval['text'] = json.loads(payload)
                    elif maintype == 'application':
                        retval['data'] = payload
                    else:
                        retval[maintype] = payload
            else:
                retval[maintype] = base64.decodestring(email_message.get_payload())
            return retval
        return None

    def write(self, fn, data):
        path = os.path.dirname(fn)
        if not os.path.isdir(config.ROOT + path):
            path = path.split('/')
            root = config.ROOT
            for p in path:
                root += '/%s'%p
                if not os.path.isdir(root):
                    os.mkdir(root)
        with open(config.ROOT + fn, 'wb') as f:
            f.write(data)

    def send(self, fn):
        text = {}
        text['filename'] = fn
        data = open(config.ROOT + fn, 'rb').read()
        text['size'] = len(data)
        m = hashlib.md5()
        m.update(data)
        text['md5'] = m.hexdigest()
        part = []
        start = 0
        while True:
            end = start + config.MAX_FILE
            if end >= text['size']:
                part.append(data[start:])
                break
            part.append(data[start:end])
            start = end
        text['total'] = len(part)

        mails = []
        msg = json.dumps(text)
        for idx, p in enumerate(part):
            mail = {}
            mail['From'] = config.FROM
            mail['To'] = config.TO
            if idx == 0:
                mail['Subject'] = fn
            else:
                mail['Subject'] = fn + '__%s'%idx
            mail['Text'] = msg
            mail['Files'] = [{
                    'filename': fn,
                    'data': p
                }]
            mails.append(mail)

        for mail in mails:
            send_mail(mail)
    
    def download(self):
        self.login()
        self.select('inbox')
        uids = self.uid(config.FROM)
        cache = {}
        for uid in uids:
            msg = self.fetch(uid)
            text = msg['text']
            if text['total'] == 1:
                self.write(text['filename'], msg['data'])
            else:
                if text['filename'] not in cache.keys():
                    cache[text['filename']] = []
                cache[text['filename']].append(msg)
                if len(cache[text['filename']])==text['total']:
                    msgs = cache.pop(text['filename'])
                    data = [None for i in range(text['total'])]
                    for msg in msgs:
                        if msg['subject'] == text['filename']:
                            data[0] = msg['data']
                        else:
                            idx = int(msg['subject'].replace(text['filename'] + '__', ''))
                            data[idx] = msg['data']
                    self.write(text['filename'], ''.join(data))

    def upload(self):
        for root, dirs, files in os.walk(config.ROOT):
            for f in files:
                fn = os.path.join(root, f).replace(config.ROOT, '')
                self.send(fn)
                
