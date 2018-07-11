"""A few utility functions used elsewhere."""

import getpass
import netrc


def get_jira_credentials(app):
    """Try to retrieve a user name and password for Jira.

    First, try reading a .netrc file. If that fails get the
    system user name and ask for a password. If this fails, too,
    give up; Jira logging will not be available.
    """
    if not _get_jira_credentials_from_netrc(app):
        if not _ask_for_credentials(app):
            print('Jira login credentials unavailable.')
            print('Assigned files can be manually copied.')


def _get_jira_credentials_from_netrc(app):
    """Try to retrieve a user name and password for Jira from .netrc."""
    try:
        nrc = netrc.netrc()
    except netrc.NetrcParseError:
        print('A .netrc file was found but there was an error parsing it.')
        return False
    except OSError as e:
        print('A .netrc file could not be found.')
        print(e)
        return False
    else:
        try:
            login, _, pwd = nrc.hosts[app.config['JIRA_URL']]
        except KeyError:
            print('No Jira credentials could be found in .netrc for URL: {}'.format(app.config['JIRA_URL']))
            return False
        else:
            app.config['JIRA_USER'] = login
            app.config['JIRA_PWD'] = pwd
            return True


def _ask_for_credentials(app):
    """ Get system user name and ask for password."""
    print('Retrieving credentials for Jira from a .netrc file failed.')
    try:
        login = getpass.getuser()
    except:
        return False
    else:
        print('We have this user name: {}'.format(login))
        print('We have this Jira URL: {}'.format(app.config['JIRA_URL']))
        pwd = getpass.getpass('This user`s password for Jira (hit RET to skip): ')
        if not pwd:
            return False
        else:
            app.config['JIRA_PWD'] = pwd
            app.config['JIRA_USER'] = login
            return True
