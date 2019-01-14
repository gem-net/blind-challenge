import os
from datetime import datetime

from flask import Flask, g, current_app
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment

from .config import config

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV') or 'default'])

bootstrap = Bootstrap()
bootstrap.init_app(app)

mail = Mail()
mail.init_app(app)

moment = Moment(app)

TABLE_DICT = {}


@app.before_request
def before_request():
    update_g()


def update_g():
    g.review = TABLE_DICT['review']


@app.before_first_request
def update_drive_listing():
    from .admin import ReviewTable

    review_folder_id = current_app.config['REVIEW_FOLDER_ID']
    review_folder_title = current_app.config['REVIEW_FOLDER_TITLE']

    TABLE_DICT.clear()
    TABLE_DICT.update({
        'review': ReviewTable(review_folder_id, review_folder_title),
    })


from .import routes
