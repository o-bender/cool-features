#!/usr/local/bin/python3.4
# -*- coding: utf-8 -*-
#from OpenSSL import SSL
from flask   import Flask
from flask   import Response
from flask   import g
from flask   import redirect
from flask   import request
from flask   import session
from flask   import render_template
from flask   import render_template_string
from flask   import url_for
from json    import dumps as json_dumps
from flask   import jsonify
from flask   import abort
from flask   import send_file

from os import listdir, remove
from os.path import isfile
from os.path import join as pjoin
from os import stat as f_stat
from os import statvfs as os_statvfs
import datetime
#from werkzeug import secure_filename # drop russian characters
from hashlib import md5
from re import compile
from re import U as re_U

import syslog
from os import fork, setuid, setgid
from setproctitle import setproctitle

from uploader import app
from urllib.parse import quote

# ---- Utils ----

re_secure_filename = compile('[\w]+', re_U)
def secure_filename(string):
    elements = re_secure_filename.findall(string)
    if len(elements):
        return '_'.join( elements[:-1] ) + '.' + elements[-1]
    return 'noname'


def getFilesList(path):
    for file_name in listdir(path):
        file_path = pjoin(path, file_name)
        if isfile(file_path):
            descr_str = ''
            ctime = datetime.datetime.fromtimestamp(f_stat(file_path).st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            yield {'name':file_name, 'cdate':ctime, 'description':descr_str, 'user':''}


def updateDownloadFiles(files):
    with open(app.config['FILES_DB'], 'w') as fp:
        fp.write('files=' + files.__str__())


def getDownloadFiles():
    from uploader.downloadfiles import files
    return files


# DL FOR Thunderburd

@app.route('/upload/purgeticket/<string:file_id>', methods=['POST'])
def dlPurgeTicket(file_id):
    files = getDownloadFiles()
    if file_id in files:
        remove(pjoin(app.config['UPLOAD_FOLDER'], file_id))
        files.pop(file_id)
        updateDownloadFiles(files)
    return 'ok', 200


@app.route('/upload/newticket', methods=['POST'])
def dlUpload():
    files = getDownloadFiles()
    if 'file' in request.files:
        file_obj = request.files['file']
        file_name = secure_filename(file_obj.filename)
        secure_link_name = md5(file_name.encode()).hexdigest()
        file_obj.save(pjoin(app.config['UPLOAD_FOLDER'], secure_link_name))

        files.update({secure_link_name: file_name})
        updateDownloadFiles(files)

        data = {'url': 'https://www.russian-kurort.ru/download/' + secure_link_name,
                'id': secure_link_name, }
        return json_dumps(data), 200
    return 400


@app.route('/upload/info')
def dlInfo():
    statvfs = os_statvfs(app.config['UPLOAD_FOLDER'])
    args = {'defaults':
        {'ticket': {
            'total':2,
            'lastdl':3,
            'maxdl':14
            }
        },
        'masterpath': 'rainbow.local',
        'maxsize': statvfs.f_frsize * statvfs.f_bfree
    }
    return json_dumps(args), 200


# Global


@app.route('/download/<string:file_link>')
def download(file_link):
    files = getDownloadFiles()
    response = Response()
    file_name = files.get(file_link)
    if file_name is None:
        return 'Файл не найден', 404
    return send_file(pjoin(app.config['UPLOAD_FOLDER'], file_link)),
                     200,
                     {'Content-Disposition': 'attachment; filename=%s' % quote(file_name, safe='')}

    if filelink in files:
        response.headers['X-Accel-Redirect'] = '/files/' + files[filelink]
        response.headers['Content-Description'] = 'File Transfer'
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Content-Type'] = 'application/octet-stream'
        response.headers['Content-Disposition'] = 'attachment; filename=%s' % files[filelink]
        return response, 200
    return response, 404
