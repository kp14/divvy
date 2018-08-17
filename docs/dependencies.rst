.. _dependencies:

Dependencies
============

Divvy depends on the following packages:

* `flask <http://flask.pocoo.org/>`_

  The web framework for this app.

* `flask-admin <http://flask-admin.readthedocs.io/en/latest/>`_ (>=1.5.1)

  Provides an admin panel for the app where the database can be administered.

* `apscheduler <https://apscheduler.readthedocs.io/en/latest/>`_

  The Advanced Python Scheduler, used for recurring tasks like checking folders.

* `flask-apscheduler <https://github.com/viniciuschiele/flask-apscheduler>`_

  Integrating APS with flask.

* `jira <https://jira.readthedocs.io/en/master/>`_

  Access to the Jira API.

* `peewee <http://docs.peewee-orm.com/en/latest/index.html>`_ (>3.0.0)

  ORM

* `wtf-peewee <https://github.com/coleifer/wtf-peewee/>`_ (>=3.0.0)
* `pbr <https://docs.openstack.org/pbr/latest/>`_
* `waitress <https://docs.pylonsproject.org/projects/waitress/en/latest/>`_

  Production-quality pure-Python WSGI server.

* `sphinx <http://www.sphinx-doc.org/en/stable/contents.html>`_ (only if docs are to be built)

Installing Divvy using ``pip`` will install its dependencies provided there is internet access.
