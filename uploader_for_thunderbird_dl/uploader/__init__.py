#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
from flask import (
    Flask
    g
    redirect
    request
    session
    render_template
    url_for
    abort
)
from functools import wraps
from werkzeug.datastructures import FileStorage
from werkzeug.contrib.fixers import ProxyFix
#from werkzeug.serving import WSGIRequestHandler

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from jinja2 import environmentfilter

#import pypostgresql

#import MySQLdb
#import MySQLdb.cursors

from sys import argv
from os import (
    fork,
    setuid,
    setgid
)
from setproctitle import setproctitle
import syslog

from hashlib import md5
from random import random
from time import time
from datetime import timedelta, datetime
#from htmlmin import minify as html_minify

# ---- Utils ----
APP_NAME = 'Uploader'
HOST = '192.168.0.19'
TCP_PORT = 21003
PROC_GROUP = 1000
PROC_USER = 1000

#DB_NAME = 'Raduga_test'
#DB_PASSWD = '1q2w3e'
#DB_USER = 'root'
#DB_HOST = 'localhost'
#DB_PORT = 3306

app = Flask(__name__)
config = app.config
config.update({
 'SESSION_COOKIE_HTTPONLY': True
,'SESSION_COOKIE_SECURE': True
#,'MAX_CONTENT_LENGTH': 5024
,'TEMPLATES_AUTO_RELOAD':False
,'SECRET_KEY': md5((time().__str__() + random().__str__()).encode()).hexdigest()
,'PERMANENT_SESSION_LIFETIME':timedelta(minutes=60)
,'FILES_DB': '/var/www/uploader_2/uploader/downloadfiles.py'
,'UPLOAD_FOLDER':'/var/www/download/files'
,'UPLOAD_ALLOWED_EXTENSIONS': set(['png', 'jpg', 'jpeg', 'gif'])
,'PID_FILE':'/var/run/uploader.pid'
})

app.wsgi_app = ProxyFix(app.wsgi_app)
#app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#app.jinja_env.globals['csrf_token'] = generateCsrfToken

# ---- Start Application ----

from uploader import views

def init(debug=None):
    if app.debug or debug:
        setproctitle(APP_NAME)
        setgid(PROC_GROUP)
        setuid(PROC_USER)
        app.run(threaded=True, host=HOST, port=TCP_PORT)
    else:
        syslog.openlog(ident=APP_NAME, logoption=syslog.LOG_PID, facility=syslog.LOG_DAEMON)
        pid = fork()
        if not pid:
    #        import ctypes
    #        libc = ctypes.cdll.LoadLibrary('libc.so.6')
    #        libc.prctl(15, 'My Simple App', 0, 0, 0)
            import sys
            setproctitle(APP_NAME)
            setgid(PROC_GROUP)
            setuid(PROC_USER)
            sys.stdout = open('/dev/null', 'w')
            sys.stderr = open('/dev/null', 'w')
#            writeLog(syslog.LOG_INFO, '%s started on %s:%d with %s' % (APP_NAME, HOST, TCP_PORT, 'user_id/group_id=%d/%d' % (PROC_USER,PROC_GROUP)))
            http_server = HTTPServer(WSGIContainer(app))
            http_server.listen(TCP_PORT)
            IOLoop.instance().start()
        with open(app.config['PID_FILE'], 'w') as fp:
            fp.write(str(pid))
#        writeLog(syslog.LOG_INFO, '%s started with PID: %d' % (APP_NAME, pid))


