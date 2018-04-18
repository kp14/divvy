.. _installation:

Installing and running Divvy in production mode
==========

Divvy is packaged as a wheel and can be installed using `pip <https://pip.pypa.io/en/stable/>`_.
This will also install all the dependencies.
Divvy uses Python 3.5.
As usual, it probably best to install divvy and its dependencies into a dedicated virtual environment.
Installation on a Linux host is assumed.

#. Create a virtual environment

    Using ``conda`` from the `Anaconda Python distribution <https://www.continuum.io/downloads>`_ :

        * Create a new environment (env) called *divvy* which runs Python 3.5 and has ``pip`` installed::

            conda create -n divvy python=3.5 pip

        * Activate the env::

            source activate divvy

    Using *venv* in a regular Python installation. Python is usually available out of the box on Linux:

        * Ensure that the version of Python used is 3.5 or higher::

            python --version

        * Create a new environment (env) called *divvy*. ``ensurepip`` will bootstrap pip into the env::

            pyvenv /path/to/new/virtual/environment/divvy

#. Install divvy with its dependencies::

        pip install Divvy-<version-py3-none-any.whl>

#. Set environment variables needed for starting divvy in production mode::

    export DIVVY_RUN=Production
    export DIVVY_SECRET_KEY=<some random key>

   .. note::
        One way to generate a 32-char long random key from the command line is
        via ``openssl rand -base64 32``.

#. Create a directory for divvy to run and store files in::

    mkdir ~/Documents/divvy
    cd divvy

#. Extract PubMed IDs from Swiss-Prot so that divvy can use them. Divvy runs fine without this but will not be able
   to determine which PubMed IDs are really new in the files submitted for QA. The script to extract the PubMed IDs
   comes packaged with divvy and should be in the PATH after installing divvy::

    pmid4divvy -f txt -o pmids_in_swissprot.txt /path/to/swissprot/flatfiles/<file_pattern>

   .. note::
        On the machine currently used for as a server for diivy, *bioborg*, the above path would be
        /mnt/f_drive/sprot/*.sp . On Linux, this has to be wrapped in single quotes. While it is
        perfectly OK to run this script manually, the ideal approach would be to schedule it using
        ``cron``. See below.

#. When running divvy for the first time, a database file will be created but it will be empty. In this case, both the
   curators' details as well as the folder to monitor have to be added manually via divvy's admin panel. If a database
   (backup) is available, the file can be used provided its name is *divvy.sqlite*.

#. Start divvy. It will be served at port 8000::

    run_divvy
    # or
    python path/to/python/env/bin/run_divvy.py

Dependencies
============

All of the following packages have to be installed some of which come with their own dependencies but those should
be taken care of by running the usual pip command:

* `flask <http://flask.pocoo.org/>`_
* `flask-admin <http://flask-admin.readthedocs.io/en/latest/>`_
* `jira <https://jira.readthedocs.io/en/master/>`_
* `peewee <http://docs.peewee-orm.com/en/latest/index.html>`_
* `wtf-peewee <https://github.com/coleifer/wtf-peewee/>`_
* `sphinx <http://www.sphinx-doc.org/en/1.4.8/>`_ (only if docs are to be built)

Changing the configuration
==========================

Apart from the ones set via environment variables as described above, all other default,
development and production configuration is contained in module config.py.
For production mode, the most likely candidates for changes are the Jira issue to write to
and the port the application is served on.
These and the other values should be self-explanatory.

Cron - pmid4divvy on a schedule
===============================

Typing ``crontab -e`` one could set a prepared script to be run every day at 7am with the following
line::

    00 07 * * * path/to/script

The script would look like this and would located in ~/Documents/divvy that we created before.
It has to be made executable using ``chmod +x <script>`` ::

    pmid4divvy -f txt -o ~/Documents/divvy '/mnt/f_drive/*.sp'

Mounting network drives
=======================

Append a line like the following to /etc/fstab::

    //server/path/to/mapped/folder /mnt/f_drive cfis credentials=/path/to/.smbcredentials,iocharset=utf8,file_mode=0777,dir_mode=0777 0 0
 
Credentials have to be provided in ~/.smbcredentials.