.. _running:

Running Divvy
=============

Following installation, a few more steps have to be taken for a proper production run.

#. Create a working directory to run Divvy in::

    mkdir ~/Documents/divvy
    cd ~/Documents/divvy

#. Set up access to a Jira instance (optional)

   On a Windows machine::

    set JIRA_URL=https://<URL of Jira instance>
    set HOME=%USERPROFILE%

#. Save Jira credentials in a .netrc file (optional)

   In the %HOME% directory, create a file called .netrc.
   Add this::

    machine https://<URL of Jira instance>
    login <Jira username>
    password <Jira password>

   If no Jira credentials are provided, automated logging of assigned files to Jira will fail but the logging text can be
   copied from within the web application, too.

#. Collect PubMed IDs from Swiss-Prot::

    set TARGET=path/to/Swiss-Prot/flat/files
    set MYENV=path/to/virtual/env
    python %MYENV%/Lib/site-packages/divvy/up2pmid.py %TARGET%/*.sp -o pmids_in_swissprot.txt

   Make sure you change into the Divvy working directory first.
   The environment variables above are only used for readability.

#. Start Divvy::

    export DIVVY_RUN=Production
    python path/to/virtual/env/Scripts.run_divvy.py

The steps above will start Divvy using the default configuration as specified in site-packages/divvy/config.py.
Parameters like the Jira issue data are logged to or the level of error reporting can be changed there.
Divvy will ask for Jira credentials if a look-up in .netrc fails and is prefectly fine running without
any connection to Jira at all.
Upon first start, the database backend (a file called divvy.sqlite, created in the working directory) will be empty.
For Divvy to work properly, the details of team members have to be provided.
This can be done via the admin panel.