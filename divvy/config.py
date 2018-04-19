# -*- coding: utf-8 -*-
"""
Created on Wed Jul 20 16:15:00 2016

@author: kp14
"""
import logging
import os
import re
import secrets
from .version import __version__

class Config(object):
    """Provides default values for configuration keys. Override as necessary.

    Accessing Jira requires a properly set up .netrc file.
    """
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'divvy.sqlite'
    SECRET_KEY = secrets.token_urlsafe(32)
    OLD_PMIDS_FILE = 'pmids_in_swissprot.txt'
    JIRA_URL = os.environ.get('JIRA_URL', 'https://not.defined')
    JIRA_USER = ''
    JIRA_PWD = ''
    PMID_REGEX = re.compile(r'PubMed=[0-9]+')
    CUR_REGEX = re.compile('\*\*Z[ABC] +[A-Z]{3}')
    HOST = '127.0.0.1'
    PORT = 7999
    LOG_FORMAT = '[%(asctime)s] %(levelname)s - %(message)s {%(pathname)s:%(lineno)d}'
    LOG_FILE = 'divvy.log'
    LOG_MAXBYTES = 100000
    LOG_BACKUP_COUNT = 1
    LOG_LEVEL = logging.DEBUG
    JOBS = [
        {
            'id': 'job1',
            'func': 'divvy.jobs:scan_folders',
            # 'args': (1, 2),
            'trigger': 'interval',
            'seconds': 20
        }
    ]
    SCHEDULER_API_ENABLED = True
    VERSION = __version__


class Production(Config):
    """Run Divvy in production mode.

    To choose this configuration, set the following ENV variables:
    DIVVY_RUN = Production
    """
    JIRA_ISSUE = 'UCR-96'
    HOST = '0.0.0.0'
    PORT = 8000
    LOG_LEVEL = logging.INFO


class Development(Config):
    """Run Divvy in development mode.

    To choose this configuration, set the following ENV variable:
    DIVVY_RUN = Development
    """
    DEBUG = True
    JIRA_ISSUE = 'UCR-2529'
