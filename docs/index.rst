.. divvy documentation master file, created by
   sphinx-quickstart on Mon Nov 14 15:28:56 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to divvy's documentation!
=================================

Divvy is a web application for assigning work for quality assurance (QA) in `UniProtKB <http://www.uniprot.org>`_ curation.

As such, it provides a graphical interface for selecting and assigning files containing UniProt entries to a person doing QA.
In addition, divvy also compiles a few numbers the team would like to keep track of - how many database entries were added
or updated and how many PubMed IDs were used to do so.

In a nutshell, the steps necessary to run this application are as follows:

#. Install Python =>3.6. If that is already the case creating a virtual environment might be best.

#. Pip install divvy and its dependencies. Divvy is packaged as a wheel and will install dependencies automatically.

#. Optional: Provide Jira login credentials in a .netrc file. The file has be located in %HOME% or, if not present, %USERPROFILE%.
   If no Jira credentials are provided, automated logging of assigned files to Jira will fail but the logging text can be
   copied from within the web application, too.

#. Create a directory to work in, e.g. F:\divvy.

#. Run the application via start script ``run_divvy``. Pip will put this into the Python distro's *Scripts* or *bin* folder.

.. toctree::
   :maxdepth: 2

   installation
   api



Indices and tables
==================


* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


