from celery import Celery
from flask import Flask
import os
import yaml


app = Flask(__name__)

if 'SETTINGS' in os.environ:
    if os.path.isfile(os.environ['SETTINGS']):
        with open(os.environ['SETTINGS'], 'r') as infile:
            app.config.update(yaml.load(infile.read()))


SETTINGS = [
    'DEBUG',
    'GITHUB_PRIVATE_KEY',
    'GITHUB_APP_ID',
    'GITHUB_WEBHOOK_SECRET',
    'CELERY_BROKER',
    'PROCESS_INSTALLS_INTERVAL']
for setting in SETTINGS:
    if setting in os.environ:
        app.config[setting] = os.environ[setting]


if 'CELERY_BROKER' in app.config:
    celery = Celery('gitconsensus', broker=app.config['CELERY_BROKER'])
else:
    celery = Celery('gitconsensus')
