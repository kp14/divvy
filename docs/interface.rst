.. _interface:

Interface and Admin panel
=========================

Interface
---------

The interface is deliberately simple:
the header contains two buttons, the body holds two tabs with a table each.
The tab *Folders* lists file data from scanned folders.
The tab *References* lists extracted PubMed IDs; these link to correspnding
abstracts at europepmc.org.

The red button *Refresh* refreshes the currently displayed data with the latest from the database.
The blue button *Update Jira with current selections* does just that.
Using only makes sense when items from the table have been selected.

At the very bottom is a small wrench icon which provides access to the admin panel.

Admin panel
-----------

The admin panel shows the version number, the timestamp of collected PMIDs from Swiss-Prot
and allows administering the backend database.