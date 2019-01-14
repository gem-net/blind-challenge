import os
import logging

from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

env_path = find_dotenv()
logger.info(env_path)
load_dotenv(env_path)


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    SERVER_NAME = os.environ.get('SERVER_NAME')

    SERVICE_ACCOUNT_FILE = os.environ.get('SERVICE_ACCOUNT_FILE')
    SCOPES = [
        'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events.readonly']
    TEAM_DRIVE_ID = os.environ.get('TEAM_DRIVE_ID')
    REVIEW_FOLDER_ID = os.environ.get('REVIEW_FOLDER_ID')
    REVIEW_FOLDER_TITLE = os.environ.get('REVIEW_FOLDER_TITLE')
    SHARED_PSWD = os.environ.get('SHARED_PSWD')


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'


class ProductionConfig(Config):
    pass


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
