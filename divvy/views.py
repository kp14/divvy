# -*- coding: utf-8 -*-
"""
This module provides are the routes in divvy.
"""
import json
from json import JSONDecodeError
from flask import (
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
    )
from divvy import app
from .models import *


@app.route("/")
def index():
    """Render the index page.

    For data to be rendered, they have to be in the database first. Database population is provided via the refresh route.

    """
    curators = Curator.select()
    checkers = Curator.select().where(Curator.checker == True)
    fldrs = Folder.select()
    ref_by_cur = compile_refs_per_curator(new=True, old=False)
    ref_by_cur_known = compile_refs_per_curator(new=False, old=True)
    ref_count = count_new_references()
    folder_count = count_files_in_folders()
    return render_template('index.html',
                           checkers=checkers,
                           curators=curators,
                           folders=fldrs,
                           ref_by_cur=ref_by_cur,
                           ref_by_cur_known=ref_by_cur_known,
                           folder_count=folder_count,
                           jira=app.config['JIRA_ISSUE'],
                           jira_url=app.config['JIRA_URL'],
                           ref_count=ref_count)


@app.route("/admin/reload_pmid", methods=['GET', 'POST'])
def reload_pmid():
    """Reload PubMed IDs from a file."""
    msg, category = read_old_pmids()
    flash(msg, category)
    return redirect(url_for('index'))


@app.route("/refresh", methods=['GET', 'POST'])
def refresh():
    """Refresh the file and reference contents of the database.

    See scan_folders for how this is done.

    Returns:
        redirect: To index.

    """
    # try:
    #     time_since_refresh = datetime.datetime.now() - app.config['OLD_PMIDS_FILE_MODIFIED']
    # except KeyError:
    #     time_since_refresh = datetime.datetime.now() - datetime.datetime(2016, 1, 1)
    # if not app.config.get('OLD_PMIDS') or time_since_refresh > datetime.timedelta(1):
    #     msg, category = read_old_pmids()
    #     flash(msg, category)
    # scan_folders()
    return redirect(url_for('index'))


@app.route('/_log_files')
def log_files():
    """Log data to JIRA instance.

    Returns:
        json: success/error message, the logged data, a message category.

    """
    files = request.args.get('files', 'None received')
    app.logger.info(type(files))
    app.logger.info('Received json for _send_mail ' + files)
    if not files or files == 'None received':
        result = 'No files received! Take a look at the logs!'
        status = "danger"
    else:
        try:
            json_data = json.loads(files)
            app.logger.info('Success - decoded JSON')
        except JSONDecodeError:
            app.logger.error('JSON not decoded!!!!!')
            result = 'JSON decoding error. Take a look at the logs!'
            status = "danger"
        else:
            ref_count = count_new_references()
            summary = summarize_new_and_updated_entries()
            comments = []
            comments.append('Files logged when: {}\n'.format(json_data['timestamp']))
            for k, v in json_data.items():
                if k not in ['timestamp']:
                    comments.append('\n{checker}:\n{files}'.format(checker=k,
                                                                   files='\n'.join(json_data[k])))
            comments.append('\nNew PMIDs: {}'.format(str(ref_count)))
            comments.append('\nUpdated Swiss-Prot: {}'.format(str(summary['swissprot'])))
            comments.append('\nNew entries: {0} (of which TrEMBL: {1} and sub/pep: {2})'.format(str(summary['trembl'] + summary['notrembl']),
                                                                                                str(summary['trembl']),
                                                                                                str(summary['notrembl'])))
            jira_comment = '\n'.join(comments)
            result = add_jira_comment(jira_comment)
            status = "success"
    return jsonify(result=result, log=jira_comment, status=status)