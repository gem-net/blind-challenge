import os
import sys
import logging
from collections import OrderedDict

from flask import Flask, g, current_app
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_login import LoginManager

from .config import config
from .models import User


app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV') or 'default'])

bootstrap = Bootstrap()
bootstrap.init_app(app)

lm = LoginManager(app)
lm.login_view = 'login'

log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format=log_format, datefmt="%Y-%m-%d %H:%M:%S")


@lm.user_loader
def load_user(user_id):
    return User()


moment = Moment(app)

TABLE_DICT = OrderedDict()


@app.before_request
def before_request():
    update_g()


def update_g():
    # get cols_show and dictionary of tables
    tables = TABLE_DICT.copy()
    cols_show = tables[next(iter(tables))].cols_show
    for i in tables:
        tables[i] = tables[i].df
    g.tables = tables
    g.cols_show = cols_show


@app.before_first_request
def update_drive_listing():
    from .admin import DriveTable

    drive_id_a = current_app.config['DRIVE_ID_A']
    drive_name_a = current_app.config['DRIVE_NAME_A']

    drive_id_b = current_app.config['DRIVE_ID_B']
    drive_name_b = current_app.config['DRIVE_NAME_B']

    TABLE_DICT.clear()
    TABLE_DICT.update({
        drive_name_a: DriveTable(drive_id_a, drive_name_a),
        drive_name_b: DriveTable(drive_id_b, drive_name_b),
    })


from .import routes
