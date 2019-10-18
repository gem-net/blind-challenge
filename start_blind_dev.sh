#!/usr/bin/env bash

# START PORTAL APP

export LC_ALL=en_US.UTF-8
export LANG=en_US.utf-8


APP_DIR=$(dirname "${BASH_SOURCE}")

source ${APP_DIR}/.env.dev

export ENV_NAME=".env.dev"
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_APP=${APP_DIR}/app.py

PORT=${PORT:-5111}

${PY_HOME}/bin/flask run --port ${PORT}
