from flask import Flask
import os
import yaml


app = Flask(__name__)

if 'SETTINGS' in os.environ:
    if os.path.isfile(os.environ['SETTINGS']):
        with open(os.environ['SETTINGS'], 'r') as infile:
            app.config.update(yaml.load(infile.read()))