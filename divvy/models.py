# -*- coding: utf-8 -*-
"""
This module defines the models used to define the database (DB) underlying Divvy as well as most business logic.
This is done using an ORM, `peewee <http://docs.peewee-orm.com/en/latest/index.html>`_.

Each model corresponds to a table in the DB. There are four models -  Curator, Folder, File and Reference.
There are several folders where files relevant to QA can be found.
Each file will have been authored by a specific curator and will be found in (at least) one folder.
Each file will also contain zero to many PubMed IDs.
As files can undergo several iterations of QA, such *resubmissions* are kept track of and filtered out in the UI.

All models that have a corresponding <model>Admin class will be exposed in divvy's admin interface.
"""
from collections import defaultdict
import datetime
import netrc
import os
import re
import time
from flask import flash
from flask_admin.contrib.peewee import ModelView
import jira
import peewee
from divvy import app, db


class MyBaseModel(peewee.Model):
    class Meta:
        database = db


class Folder(MyBaseModel):
    """Model a folder containing files for QA.

    Attributes:
        path (str): Fully qualified folder path.

    """
    path = peewee.CharField(max_length=100)

    def __unicode__(self):
        return self.path


class Curator(MyBaseModel):
    """Model a curator (user) who authors and submits files for QA.

    Attributes:
        surname (str): Curator's surname.
        given_name (str): Curator's given name.
        initial (str): Three-letter abbreviation of curator's name as used in UniProtKB.
        checker (bool): Whether a curator participates in QA.

    """
    surname = peewee.CharField(max_length=100)
    given_name = peewee.CharField(max_length=100)
    initial = peewee.FixedCharField(max_length=3)
    checker = peewee.BooleanField()

    def __unicode__(self):
        return "{0}, {1}".format(self.surname, self.given_name)


class File(MyBaseModel):
    """Model a file which contains content to be checked in QA.

    Attributes:
        filename (str): A file's name including extension but not the path.
        filetype (str): A file name extension.
        checksum (str): Checksum based on file's name and content.
        curator (foreignkey): Pointer to Curator table.
        folder (foreignkey): Pointer to Folder table.
        entry_count (int): Number of UniProtKB entries contained within a file.
        resubmission (bool): Whether a file has been through QA before.

    """
    filename = peewee.CharField(max_length=50)
    filetype = peewee.FixedCharField(max_length=3)
    checksum = peewee.CharField()
    curator = peewee.ForeignKeyField(Curator, related_name='submitted_files')
    folder = peewee.ForeignKeyField(Folder, related_name='files')
    entry_count = peewee.IntegerField()
    resubmission = peewee.BooleanField()

    def __unicode__(self):
        return self.filename


class Reference(MyBaseModel):
    """Model a reference as identified by its PubMed ID.

    References which do not have a PubMed ID are ignored although they might be valid publications. This is due to
    the PubMed indexing which does not capture all papers.

    Attributes:
        pmid (str): PubMed identifier, a string of numbers.
        sourcefile (foreign key): Pointer to File table.
        is_new (bool): Whether a reference is already in Swiss-Prot.

    """
    pmid = peewee.CharField(max_length=20)
    sourcefile = peewee.ForeignKeyField(File, related_name='references', on_delete='CASCADE')
    is_new = peewee.BooleanField()

    def __unicode__(self):
        return self.pmid


class CuratorAdmin(ModelView):
    pass


class FolderAdmin(ModelView):
    pass


class FileAdmin(ModelView):
    pass


class ReferenceAdmin(ModelView):
    pass


def count_files_in_folders():
    """Count entries contained in files on a per folder basis excluding resubmissions.

    Sum up entry counts per File in the File table and aggregate by Folder. Resubmissions are excluded.

    """
    fldrs = (Folder
             .select(Folder.path, peewee.fn.Sum(File.entry_count).alias('count'))
             .join(File)
             .where(File.resubmission==False)
             .group_by(Folder.path))
    d = {}
    for fldr in fldrs:
        d[fldr.path] = fldr.count
    return d


def summarize_new_and_updated_entries():
    """Provide a summary of total new/sub entries and updated entries.
    
    Returns:
        dict: keys - trembl, notrembl, swissprot 
    """
    fldr_count = count_files_in_folders()
    summary = {'swissprot': 0,
               'notrembl': 0,
               'trembl': 0,
               }
    for k, v in fldr_count.items():
        if k.endswith('various'):
            summary['swissprot'] = v
        elif k.endswith('upd'):
            summary['notrembl'] = v
        elif k.endswith('new'):
            summary['trembl'] = v
    return summary

def compile_refs_per_curator(new=True, old=True):
    """Compile all DISTINCT reference PMIDs for each curator which are not resubmissions.
    
    Attributes:
        new (bool): Whether to consider PMIDs not yet in Swiss-Prot. Default: True.
        old (bool): whether to consieder PMIDs already in Swiss-Prot. Default: True.

    Returns:
        dict, {given_name: set(PMIDs)}
    """
    ref_by_cur = defaultdict(set)
    curators = Curator.select()
    for curator in curators:
        for file in curator.submitted_files:
            if not file.resubmission:
                if new and old:
                    for ref in file.references:
                       ref_by_cur[curator.given_name].add(ref.pmid)
                elif new and not old:
                    for ref in file.references:
                        if ref.is_new:
                            ref_by_cur[curator.given_name].add(ref.pmid)
                elif old and not new:
                    for ref in file.references:
                        if not ref.is_new:
                            ref_by_cur[curator.given_name].add(ref.pmid)
                else:
                    ref_by_cur[curator.given_name] = set()
    return ref_by_cur


def count_new_references():
    """Count all new PMIDs, ignoring those from large scale projects or resubmissions.
    
    Returns:
        int
    """
    ref_count = (Reference
                 .select(peewee.fn.Count(peewee.fn.Distinct(Reference.pmid)).alias('count'))
                 .join(File)
                 .where(File.resubmission == False, Reference.is_new == True))
    return ref_count[0].count


def add_jira_comment(comment):
    """Log data to JIRA.

    The JIRA instance, issue and credentials are specified via config.py.

    Returns:
        str: An error or a success message.
    """
    if not app.config['JIRA_PWD']:
        return 'Cannot log to Jira. Click here!'
    else:
        try:
            ucr = jira.JIRA(app.config['JIRA_URL'], basic_auth=(app.config['JIRA_USER'],
                                                                app.config['JIRA_PWD']))
        except:
            return 'Cannot log to Jira. Click here!'
        else:
            app.logger.info('Logged into JIRA')
            ucr.add_comment(app.config['JIRA_ISSUE'], comment)
            app.logger.info('Comment added to {}'.format(app.config['JIRA_ISSUE']))
            return 'Jira updated!'


def read_old_pmids():
    """Load PubMed IDs from a file.

    The path to the file is set in config.py. The file is expected to contain one PubMed ID per line.

    Returns:
        tuple: A success/error message and a corresponding message category.

    """
    pmid_set = set()
    category = 'alert alert-info'
    msg = ''
    try:
        _ = app.config['OLD_PMIDS_FILE_MODIFIED']
    except KeyError:
        app.config['OLD_PMIDS_FILE_MODIFIED'] = datetime.datetime(2016, 1, 1)
    try:
        with open(app.config['OLD_PMIDS_FILE'], 'r', encoding='utf8') as f:
            for line in f:
                pmid_set.add(line.strip())
    except FileNotFoundError:
        app.logger.error('PMIDs already in Swiss-Prot could not be loaded!')
        app.logger.error('Reported PMIDs will not necessarily be new!')
        category = 'alert alert-danger'
        msg = 'PMIDs could not be loaded. File not found.'
    else:
        app.config['OLD_PMIDS_FILE_MODIFIED'] = datetime.datetime.fromtimestamp(
            os.path.getmtime(app.config['OLD_PMIDS_FILE']))
        msg = '{0} PMIDs loaded. Data gathered when: {1}'.format(str(len(pmid_set)),
                                                                 app.config['OLD_PMIDS_FILE_MODIFIED'].ctime())
        if pmid_set:
            app.logger.info(msg)
            category = 'alert alert-success'
        else:
            app.logger.warn(msg)
            category = 'alert alert-warning'
    finally:
        app.config['OLD_PMIDS'] = pmid_set
        return (msg, category)




