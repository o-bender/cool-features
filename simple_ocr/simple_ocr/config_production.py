from logging import INFO 


class Config:
    APP_NAME = 'Simple OCR'
    PROC_GROUP = 1000
    PROC_USER = 1000
    UPLOAD_FOLDER = '/var/www/simple_ocr/tmp'
    ALLOWED_FILES = {'jpg', 'jpeg', 'png', 'tiff', 'tif', 'pdf'}
    THRESHOLD_LIFETIME = 1
    TCP_PORT = 9001

    LOGGING_FILE = 'log.log'
    LOG_MAX_BYTES = 1024 * 100
    LOG_MAX_BACKUP_COUNT = 4
    LOG_LEVEL = INFO
