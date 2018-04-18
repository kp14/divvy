# -*- coding: utf-8 -*-
"""
Divvy.py

Divvy the work up on Thursdays.

Created on Thu May 12 14:22:01 2016

@author: kp14
"""
import logging
from logging.handlers import RotatingFileHandler
import os
import peewee
from flask import Flask


app = Flask(__name__)
run_status = os.environ.get('DIVVY_RUN', 'Development')
app.config.from_object('divvy.config.{}'.format(run_status))


app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(app.config['LOG_FORMAT'])
handler = RotatingFileHandler(app.config['LOG_FILE'],
                              maxBytes=app.config['LOG_MAXBYTES'],
                              backupCount=app.config['LOG_BACKUP_COUNT'])
handler.setLevel(app.config['LOG_LEVEL'])
handler.setFormatter(formatter)
app.logger.addHandler(handler)


db = peewee.SqliteDatabase(app.config['DATABASE_URI'], check_same_thread=False, pragmas=(('foreign_keys', 'on'),))

