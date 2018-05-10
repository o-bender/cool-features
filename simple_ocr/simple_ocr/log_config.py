import logging
import os

from logging.handlers import RotatingFileHandler, SysLogHandler  # , SMTPHandler
from logging import Formatter


def set_up_logging(app):
    # if not app.debug:
    #     mail_handler = SMTPHandler(
    #         mailhost=(app.config['MAIL_SERVER'],
    #         app.config['MAIL_PORT']),
    #         fromaddr=app.config['MAIL_DEFAULT_SENDER'],
    #         toaddrs=app.config['ADMINS'],
    #         subject=app.config['SERVER_NAME_FOR_LOG'] + ' - Your Application Failed',
    #         credentials=(
    #             app.config['MAIL_USERNAME'],
    #             app.config['MAIL_PASSWORD']
    #         ),
    #         secure=()
    #     )
    #     mail_handler.setLevel(logging.ERROR)
    #     app.logger.addHandler(mail_handler)
    #     logging.getLogger('werkzeug').addHandler(mail_handler)

    if app.config['LOGGING_FILE'].lower() == 'syslog':
        file_handler = SysLogHandler()
    else:
        file_handler = RotatingFileHandler(app.config['LOGGING_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_MAX_BACKUP_COUNT'])

    file_handler.setLevel(app.config['LOG_LEVEL'])
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)
    logging.getLogger('werkzeug').addHandler(file_handler)

    if not app.config['DEBUG']:
        stream = logging.StreamHandler()
        stream.setLevel(logging.INFO)
        logging.basicConfig(level=logging.DEBUG, handlers=[stream])
        app.logger.addHandler(stream)

    if not os.environ.get("FLASK_DEBUG"):
        logging.basicConfig(level=logging.INFO, handlers=[file_handler])

    formatter = Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    for handler in app.logger.handlers:
        handler.setFormatter(formatter)

    app.logger.info("Application started")
