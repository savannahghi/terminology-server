# coding=utf-8
"""Get the content from a predefined Dropbox folder"""
__author__ = 'ngurenyaga'
import os
import json
import logging
import zipfile
import dropbox

from django.core.management.base import BaseCommand
from django.core.exceptions import ValidationError
from django.conf import settings

# The bulky SNOMED content is kept on DropBox ( too big for GIT )
DROPBOX_SNOMED_FOLDER_URL = \
    'https://www.dropbox.com/sh/zxg5mkeibq2sp14/AACSO2Bc4iNyi27pxcWAwNb3a?dl=0'
DROPBOX_APP_KEY = 'fyukmm3h0a65ssv'
DROPBOX_APP_SECRET = 'oslxpyyajgcoqqi'
DROPBOX_ACCESS_TOKEN = \
    'eriIgWvfTBQAAAAAAAAHrOy2aZxAzWpeu-CI6XsmzM0zBmT5LqpdkygcLM1SIs1y'

WORKING_FOLDER = os.path.join(
    os.path.dirname(settings.BASE_DIR), 'source_terminology_data')
EXTRACT_WORKING_FOLDER = os.path.join(
    os.path.dirname(settings.BASE_DIR), 'extracted_terminology_data')
METADATA_FILE = os.path.join(WORKING_FOLDER, 'metadata.json')

LOGGER = logging.getLogger(__name__)

# Create the working folders if they do not exist
if not os.path.exists(WORKING_FOLDER):
    os.mkdir(WORKING_FOLDER)
if not os.path.exists(EXTRACT_WORKING_FOLDER):
    os.mkdir(EXTRACT_WORKING_FOLDER)

# Sanity check; it must be a directory
if not os.path.isdir(WORKING_FOLDER):
    raise ValidationError('The folder %s does not exist' % WORKING_FOLDER)


class Command(BaseCommand):
    """The SNOMED content is too large to be distributed via GIT"""
    help = 'Fetch the current SNOMED content from Dropbox'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.client = dropbox.client.DropboxClient(DROPBOX_ACCESS_TOKEN)
        self.upstream_metadata = self.client.metadata('/snomed_source_files')

        self.stored_metadata = self.get_stored_metadata()
        self.path_keyed_upstream_metadata = {
            entry['path']: entry for entry in
            self.upstream_metadata['contents']
        }
        self.path_keyed_stored_metadata = {
            entry['path']: entry for entry in self.stored_metadata['contents']
        } if self.stored_metadata else {}

    def get_stored_metadata(self):
        """In a fresh install, it needs to be run twice"""
        if os.path.exists(METADATA_FILE):
            with open(METADATA_FILE) as f:
                return json.load(f)
        # Default exit
        return None

    def fetch_file(self, file_path):
        """Download the file at file_path ( relative to app's Dropbox root )"""
        # Extract the last part of the filename from the path
        try:
            new_file_name = os.path.basename(file_path)
            new_file_path = os.path.join(
                WORKING_FOLDER, new_file_name)
            with open(new_file_path, 'wb') as out_file:
                with self.client.get_file(file_path) as in_file:
                    out_file.write(in_file.read())

            LOGGER.info('Downloaded %s from Dropbox' % new_file_path)
        except:
            LOGGER.info('Unable to fetch %s from Dropbox' % file_path)
            try:
                os.remove(new_file_path)
                LOGGER.info('Deleted %s [ clean up ]' % new_file_path)
            except:
                LOGGER.info('Cannot delete %s [ clean up ]' % new_file_path)

    def save_metadata(self, metadata_dict):
        """Save the newest metadata to file"""
        with open(METADATA_FILE, 'w') as f:
            f.write(json.dumps(metadata_dict, indent=4))
        LOGGER.info('Saved metadata')

    def file_has_changed(self, file_path):
        """Return True if a file has changed, otherwise False"""
        if file_path not in self.path_keyed_upstream_metadata:
            raise Exception('Inconsistent state; should not occur')

        if file_path not in self.path_keyed_stored_metadata:
            LOGGER.info('%s appears to be a new file' % file_path)
            return True  # We have not seen this file before

        expected_file_path = os.path.join(
            WORKING_FOLDER, os.path.basename(file_path))
        if not os.path.exists(expected_file_path):
            LOGGER.info('Cannot find expected file %s' % expected_file_path)
            return True

        upstream_file_metadata = self.path_keyed_upstream_metadata[file_path]
        stored_file_metadata = self.path_keyed_stored_metadata[file_path]
        keys = ['bytes', 'rev', 'revision', 'size', 'path', 'mime_type']

        for key in keys:
            if (key not in upstream_file_metadata
                    or key not in stored_file_metadata):
                raise Exception(
                    'The key %s was not found in a metadata dict' % key)

            if upstream_file_metadata[key] != stored_file_metadata[key]:
                LOGGER.info('Found a change in key %s for path %s' %
                            (key, file_path))
                return True

    def metadata_has_changed(self):
        """Return True if there is a change; otherwise False"""
        upstream_contents = self.upstream_metadata['contents']
        stored_contents = self.stored_metadata['contents']
        if not self.stored_metadata:
            LOGGER.info('No stored metadata; assumed to be a new installation')
            return True  # We assume that it is a new installation
        else:
            if (len(upstream_contents) != len(stored_contents)):
                LOGGER.info('The no of files is different upstream/downstream')
                return True  # There has been a change in the number of files

            for entry in upstream_contents:
                if self.file_has_changed(entry['path']):
                    LOGGER.info('%s has changed' % entry['path'])
                    return True  # If any file has changed, exit early

        # Default exit
        return False

    def get_upstream_file_paths(self):
        """Produce an iterator of paths to non-dir files upstream"""
        return (
            entry['path'] for entry in self.upstream_metadata['contents']
            if not entry['is_dir']
        )

    def get_cached_file_paths(self):
        """Produce an iterator of paths to non-dir files in the local folder"""
        # In a fresh install, this will initially have been null
        if not self.stored_metadata:
            self.stored_metadata = self.get_stored_metadata()
        return (
            entry['path'] for entry in self.stored_metadata['contents']
            if not entry['is_dir']
        )

    def extract_zips(self):
        """(Re-)extract the downloaded SNOMED distribution zipfiles"""
        # Extract zips afresh each time there is a change
        current_files = os.listdir(EXTRACT_WORKING_FOLDER)
        for current_file in current_files:
            if not os.is_dir(current_file):
                os.remove(current_file)
            else:
                os.rmdir(current_file)

        source_file_paths = self.get_cached_file_paths()
        for source_file_path in source_file_paths:
            if source_file_path.endswith('.zip'):
                zf = zipfile.ZipFile(
                    WORKING_FOLDER +
                    source_file_path.replace('snomed_source_files', ''), 'r')
                entries = zf.namelist()
                LOGGER.debug(
                    '%s has the following files: %s' %
                    (source_file_path, entries))
        # TODO Extract the metadata from each
        # TODO Extract the content from each and save

    def handle(self, *args, **options):
        """The command's entry point"""
        # First, synchronize with Dropbox
        if self.metadata_has_changed():
            # Save the new metadata
            LOGGER.info('Metadata has changed, saving the current state')
            self.save_metadata(self.upstream_metadata)

            # Check which files have changed upstream and queue for download
            for upstream_file_path in self.get_upstream_file_paths():
                if self.file_has_changed(upstream_file_path):
                    LOGGER.info('Fetching %s' % upstream_file_path)
                    self.fetch_file(upstream_file_path)

            self.extract_zips()
        else:
            LOGGER.info(
                'There is no change in the Dropbox folder. '
                'Happy to do nothing! However, '
                'if your "%s" or "%s" folders are inconsistent, delete '
                'them and re-run this command' %
                (WORKING_FOLDER, EXTRACT_WORKING_FOLDER)
            )

        # TODO Remove this, it is a temporary debugging aid
        self.extract_zips()


        # TODO Update README to reflect new layout ( or remove it altogether )
        # TODO Update discover to now work with the default layout
