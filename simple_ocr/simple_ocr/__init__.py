from flask import Flask, render_template, flash, request, send_file, url_for
from subprocess import Popen
from subprocess import PIPE
from os import remove, mkdir, path
from time import sleep
from io import BytesIO
from simple_ocr.config_production import Config as ConfigProduction
from setproctitle import setproctitle
from os import fork, setuid, setgid, path, listdir, environ
from tempfile import mktemp
import traceback
import shutil
from urllib.parse import quote
from itsdangerous import URLSafeSerializer
import json


app = Flask(__name__)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


def TextResponse(message, code=200, headers={}):
    headers.update({'Content-Type': 'text/plain'})
    return message, code, headers


def JsonResponse(data, code=200, headers={}):
    headers.update({'Content-Type': 'application/json'})
    if type(data) == str:
        return data, code, headers
    else:
        return json.dumps(data, cls=DecimalEncoder), code, headers


def setProcParams(app):
    setproctitle(app.config['APP_NAME'])
    setgid(app.config['PROC_GROUP'])
    setuid(app.config['PROC_USER'])


def init_app(app):
    app.config.from_object(ConfigProduction)
    # setProcParams(app)
    return app


def teseract_ocr(file_path):
    proc = Popen(['/bin/sh', '/var/www/simple_ocr/ocr.sh', file_path, path.dirname(file_path), '-density', '300'],
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE
    )
    out, err = proc.communicate()
    if b'Killed' in err:
        proc = Popen(['/bin/sh', '/var/www/simple_ocr/ocr.sh', file_path, path.dirname(file_path)],
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE
        )
        out, err = proc.communicate()
    app.logger.info('{}\n{}'.format(out, err))
    proc.wait()


def ocr(file):
    s_filename = file.filename.split('.')
    tmp_name = mktemp(dir='')
    tmp_filename = '%s.%s' % (tmp_name, s_filename[-1])
    tmp_dir = path.join(app.config['UPLOAD_FOLDER'], tmp_name)
    tmp_filepath = path.join(tmp_dir, tmp_filename)
    out_filename = '%s.docx' % '.'.join(s_filename[0:-1])

    mkdir(tmp_dir)
    file.save(tmp_filepath)

    try:
        teseract_ocr(tmp_filepath)
    except Exception as e:
        app.logger.warning(e)
        app.logger.warning(traceback.format_exc())
        return {'error': str(e)}

    return {'filename': out_filename, 'file': path.join(tmp_dir, '%s.docx' % tmp_name)}


def allowed_files(filename):
    return filename.split('.')[-1].lower() in app.config['ALLOWED_FILES']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if file or allowed_files(file.filename):
            ocr_data = ocr(file)

            if ocr_data.get('error'):
                return JsonResponse(ocr_data)

            s = URLSafeSerializer(app.secret_key or 'somekey', salt='get_file')
            return JsonResponse({
                'link': url_for('get_file', token=s.dumps(ocr_data)),
                'filename': ocr_data['filename']})
        else:
            return JsonResponse({'error': 'Некорректный тип файла'})
    return render_template('body.html')


@app.route('/download/<string:token>')
def get_file(token):
    s = URLSafeSerializer(app.secret_key or 'somekey', salt='get_file')
    data = s.loads(token)

    with open(data['file'], 'rb') as fp:
        bytes_data = fp.read()
    stream = BytesIO(bytes_data)

    # shutil.rmtree(path.dirname(data['file']))
    
    return send_file(
        stream,
        attachment_filename=quote(data['filename'].encode('utf-8')),
        as_attachment=True)
