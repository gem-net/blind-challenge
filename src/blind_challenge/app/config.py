import os
import logging

from dotenv import load_dotenv, find_dotenv

logger = logging.getLogger(__name__)

env_path = os.getenv('ENV_NAME', find_dotenv())
logger.info("Loading .env from %s", env_path)
load_dotenv(env_path, override=True)


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
    CREDENTIALS_AS_USER = os.environ.get('CREDENTIALS_AS_USER')
    SHARED_PSWD = os.environ.get('SHARED_PSWD')
    CHALLENGE_NAME = os.environ.get('CHALLENGE_NAME')
    DRIVE_ID_A = os.environ.get('DRIVE_ID_A')
    DRIVE_ID_B = os.environ.get('DRIVE_ID_B')
    DRIVE_NAME_A = os.environ.get('DRIVE_NAME_A')
    DRIVE_NAME_B = os.environ.get('DRIVE_NAME_B')


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
