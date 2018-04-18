#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tying it all together.

@author: kp14
"""
import flask_admin as admin
from flask_apscheduler import APScheduler
from waitress import serve
from divvy import app, db
from divvy.models import *
from divvy.views import *


admin = admin.Admin(app, name='Divvy:admin')
admin.add_view(CuratorAdmin(Curator))
admin.add_view(FolderAdmin(Folder))
admin.add_view(FileAdmin(File))
admin.add_view(ReferenceAdmin(Reference))

# Delete any leftover file and reference data
db.drop_tables([File, Reference])
# Only create the tables if they do not exist.
db.create_tables([Curator, Folder, File, Reference], safe=True)

if __name__ == "__main__":
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    serve(app,
          host=app.config['HOST'],
          port=app.config['PORT'],
          )
