mail-disk
=========

将邮箱作为网盘

Usage:
=====

    mv config.sample.py config.py
    python main.py download # 下载邮件中的文件
    python main.py upload # 上传文件

config.py:
=========

    # sendmail part
    FROM = 'lupino <lupino@yopmail.com>'
    TO = ['you email adress']
    MAX_MAIL = 2048000 # 最大邮件 限制
    MAX_FILE = MAX_MAIL/2 
    ROOT = 'root'
    
    # receive part
    IAMP_HOST = ''
    IAMP_USER = ''
    IAMP_PASSWD = ''
    SSL = True
