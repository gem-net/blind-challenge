from collections import OrderedDict
from datetime import date, datetime, timezone, timedelta

import pandas as pd
from flask import current_app
from google.oauth2 import service_account
from googleapiclient.discovery import build
# from httplib2 import Http
# from oauth2client import file, client, tools

from .helpers import parse_timestamp_str
from .drive import file_tree_to_df


def get_service_handles():
    """Get dictionary of {service_name: service_handle}."""
    SERVICE_ACCOUNT_FILE = current_app.config['SERVICE_ACCOUNT_FILE']
    # GROUP_KEY = current_app.config['GROUP_KEY']
    SCOPES = current_app.config['SCOPES']

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(
        current_app.config['CREDENTIALS_AS_USER']
    )

    files_service = build('drive', 'v3', credentials=delegated_credentials,
                          cache_discovery=False)
    return {
        'files': files_service,
    }


SERVICE_HANDLES = get_service_handles()


class ApiTable:
    cols_show = None  # subclasses will override
    cols_other = None

    def __init__(self):
        self._df = None  # subclasses will override
        self.last_refresh = datetime.utcnow()
        self.refresh_minutes = 1
        self.refresh_df()

    def refresh_df(self):
        """Subclasses will override this method."""
        pass

    @property
    def cols(self):
        return list(self.cols_show) + list(self.cols_other)

    @property
    def df(self):
        if datetime.utcnow() > (self.last_refresh + timedelta(minutes=self.refresh_minutes)):
            self.refresh_df()
            self.last_refresh = datetime.utcnow()
        return self._df

    @staticmethod
    def _get_utc_naive(dt):
        """Convert timezone aware timestamp to UTC naive timestamp."""
        return dt.astimezone(timezone.utc).replace(tzinfo=None)


class DriveTable(ApiTable):

    def __init__(self, root_folder_id, root_folder_title):
        self.refresh_minutes = 5
        self.root_folder_id = root_folder_id
        self.root_folder_title = root_folder_title
        super().__init__()

    cols_show = OrderedDict([
        ('title', 'Document'),
        ('date_modified', 'Modified'),
    ])
    cols_other = ['path', 'path_show', 'date_created', 'icon', 'id', 'kind',
                  'last_user', 'mimeType', 'thumb', 'url_content', 'url_view']

    def refresh_df(self):
        files = file_tree_to_df(self.root_folder_id, self.root_folder_title)
        if len(files):
            cols_present = [i for i in DriveTable.cols_other if i in files.columns]
            files = files[list(DriveTable.cols_show) + cols_present]
            files = files.sort_values(['path', 'mimeType', 'title'])
        self._df = files
