import datetime
import hashlib
import pathlib
import os
import re
from collections import deque
from flask import flash
from divvy import app, db
from divvy.models import Curator, File, Folder, Reference, read_old_pmids

MONITOR_QUEUE = deque([{}], maxlen=2)


def scan_folders():
    """Extract file data for QA.

    This is the workhorse function. It re-compiles information on files and references contained in them.
    Previous records of files and references are wiped at the start.

    """
    _load_swissprot_pubmed_ids()
    reference_models = []
    _survey_files_in_folders()
    _delete_obsolete_files()
    for wrapped_path in files2add():
        file_model_dict = _extract_file_data(wrapped_path)
        app.logger.debug('Prepared dict for file: {}'.format(str(wrapped_path.path)))
        app.logger.debug((file_model_dict))
        with db.atomic():
            File.insert(**file_model_dict).execute()
            app.logger.debug('Inserted File into db: {}'.format(str(wrapped_path.path)))
        reference_models_temp = _extract_pmids(wrapped_path)
        reference_models.extend(reference_models_temp)
        app.logger.debug('Prepared pmid dict for file: {}'.format(str(wrapped_path.path)))
    if reference_models:
        app.logger.info('Collected {} references to write to DB.'.format(str(len(reference_models))))
        with db.atomic():
            Reference.insert_many(reference_models).execute()
    else:
        app.logger.warn('No references collected to add to DB.')


class WrappedPath(object):
    """Wraps a Pathlib object.

    Allows to add more attributes as PurePath-derived objects
    use slots.
    """
    def __init__(self, path):
        self.path = path
        self.checksum = self._compute_checksum_for_file()

    def _compute_checksum_for_file(self):
        """Compute md5 of file name and content.

        Returns:
            hexdigest of checksum (str)
        """
        cs = hashlib.md5()
        cs.update(self.path.read_bytes())
        cs.update(bytes(self.path))
        return cs.hexdigest()


def _load_swissprot_pubmed_ids():
    try:
        time_since_refresh = datetime.datetime.now() - app.config['OLD_PMIDS_FILE_MODIFIED']
    except KeyError:
        time_since_refresh = datetime.datetime.now() - datetime.datetime(2016, 1, 1)
    if not app.config.get('OLD_PMIDS') or time_since_refresh > datetime.timedelta(1):
        msg, category = read_old_pmids()
        # flash(msg, category)


def _check_whether_resubmission(pth):
    """Check whether a given file is a resubmission.

    Args:
        pth: WrappedPath object.

    Returns:
        bool

    """
    app.logger.debug('_check_whether_resubmission: {}'.format(pth.path))
    return 'resub' in str(pth.path)


def _count_entries_in_file(pth):
    """Count the number of Uniprot entries in a file.

    We use //, the end-of-entry delimiter, as a measure. In LOG files this might underestimate numbers but that is
    accepted.

    Args:
        pth: WrappedPath object.

    Returns:
        int: Entry count.

    """
    app.logger.debug('_count_entries_in_file: {}'.format(str(pth.path)))
    try:
        file_content = pth.path.read_text()
        count = len(re.findall('\n//', file_content))
    except PermissionError:
        count = 0
        app.logger.error('No permission to access file: {}'.format(str(pth.path)))
    finally:
        return count


def _find_curator_initials(pth):
    """Initials allow us to then retrieve a Curator

        Args:
            pth: WrappedPath object.

        Returns:
            str: Initials or None
        """
    initials = None
    regex = app.config['CUR_REGEX']
    file_content = pth.path.read_text()
    curator_match = re.search(regex, file_content)
    if curator_match:
        initials = curator_match.group(0).split()[1]
    return initials


def _find_curator(pth):
    """Identify who authored entries contained in file.

    Args:
        pth: WrappedPath object.

    Returns:
        model instance: Curator model instance.

    """
    curator_initial = _find_curator_initials(pth)
    if curator_initial:
        try:
            curator_model_instance = Curator.select().where(Curator.initial == curator_initial).get()
            app.logger.info('Curator found for file: {}'.format(str(pth.path)))
        except:
            app.logger.warn('No curator found for initial: {}'.format(curator_initial))
            curator_model_instance = Curator.select().where(Curator.initial == 'XYZ').get()
    else:
        # Assign this to 'Nobody'
        curator_model_instance = Curator.select().where(Curator.initial == 'XYZ').get()
        app.logger.warn('No curator found for file: {}'.format(str(pth.path)))
    return curator_model_instance


def _find_folder(pth):
    """Get Folder model instance for file.

    Args:
        pth: WrappedPath object.

    Returns:
        model instance: Folder
    """
    folder_model_instance = Folder.select().where(Folder.path == str(pth.path.parent)).get()
    return folder_model_instance


def _extract_pmids(pth):
    """Extract PubMed IDs from entries.

    Args:
        pth: WrappedPath object.

    Returns:
        list: List of dicts describing Reference model instances.

    """
    rp_tmp = []
    pmid_set_tmp = set()
    reference_model_list =[]
    with open(pth.path, 'r', encoding='latin1') as f:
        for line in f:
            prefix, rest = line[:2], line[5:].rstrip()
            if prefix == 'RP':
                rp_tmp.append(rest)
            if prefix == 'RL':
                rp_tmp = []
            if prefix == 'RX':
                rp_line = ' '.join(rp_tmp)
                if 'LARGE SCALE' in rp_line:
                    app.logger.warn('Ignored LARGE SCALE ref: {}'.format(rest))
                    app.logger.info('RP line for above reference: {}'.format(rp_line))
                else:
                    match = re.search(app.config['PMID_REGEX'], rest)
                    if match:
                        pmid = match.group(0)[7:]
                        pmid_set_tmp.add(pmid)
    new_pmids = pmid_set_tmp.difference(app.config['OLD_PMIDS'])
    known_pmids = pmid_set_tmp.intersection(app.config['OLD_PMIDS'])
    if known_pmids:
        for item in known_pmids:
            app.logger.info('Found previously used PMID for file {0}: {1}'.format(pth.path, item))
    file_model_instance = File.select().where(File.filename == pth.path.name).get()
    for pmid in new_pmids:
        reference_model_list.append({'pmid': pmid, 'sourcefile': file_model_instance.id, 'is_new': True})
    for pmid in known_pmids:
        reference_model_list.append({'pmid': pmid, 'sourcefile': file_model_instance.id, 'is_new': False})
    return reference_model_list


def _extract_file_data(pth):
    """Extract metadata of file in path.

    Args:
        pth: WrappedPath object

    Returns:
        dict: Dict describing a File model instance.

    """
    file_model_dict = {}
    file_model_dict['filename'] = pth.path.name
    file_model_dict['filetype'] = pth.path.suffix
    file_model_dict['checksum'] = pth.checksum
    file_model_dict['curator'] = _find_curator(pth).id
    file_model_dict['folder'] = _find_folder(pth).id
    file_model_dict['entry_count'] = _count_entries_in_file(pth)
    file_model_dict['resubmission'] = _check_whether_resubmission(pth)
    return file_model_dict


def _survey_files_in_folders():
    """Compile checksums for files.

    Values are stored in the modules level variable
    MONITOR_QUEUE.
    """
    checksum_dict = {}
    for folder_instance in Folder.select():
        current_folder = pathlib.Path(folder_instance.path)
        app.logger.info('Looking at folder: {}'.format(str(current_folder)))
        if not current_folder.exists():
            msg = 'There was an error accessing {}'.format(str(current_folder))
            category = 'alert alert-danger'
            # flash(msg, category)
            app.logger.error(msg)
        else:
            file_list = [WrappedPath(x) for x in current_folder.iterdir() if x.is_file()]
            for f in file_list:
                app.logger.info('File: {0} - Checksum: {1}'.format(str(f.path), f.checksum))
                checksum_dict[f.checksum] = f
    MONITOR_QUEUE.append(checksum_dict)


def _files2delete():
    """Determine which File model instances have to be deleted.

    Returns:
        generator (File): File model instance.
    """
    previous = set(MONITOR_QUEUE[0].keys())
    current = set(MONITOR_QUEUE[1].keys())
    for checksum in previous.difference(current):
        file_model_instance = File.select().where(File.checksum == checksum).get()
        yield file_model_instance


def _delete_obsolete_files():
    for file_model in _files2delete():
        app.logger.info('Deleted file from db: {}'.format(file_model.path))
        file_model.delete_instance(recursive=True)


def files2add():
    """Determine which files to add to the database.

    Returns:
        generator (str): pathlib.Path objects.
    """
    previous = set(MONITOR_QUEUE[0].keys())
    current = set(MONITOR_QUEUE[1].keys())
    for checksum in current.difference(previous):
        yield MONITOR_QUEUE[1][checksum]
