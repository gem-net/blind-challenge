from collections import OrderedDict
import io
import logging

import pandas as pd
import networkx as nx
from googleapiclient.http import MediaIoBaseDownload

from .helpers import parse_timestamp_str


logger = logging.getLogger(__name__)

MIME_MAP = {
    'application/vnd.google-apps.spreadsheet':
        ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', '.xlsx'),  # Google Sheets
    'application/vnd.google-apps.document': ('application/pdf', '.pdf'),  # Google Docs
    'application/vnd.google-apps.presentation': ('application/pdf', '.pdf'),  # Google Slides
}


class Folder:
    def __init__(self, folder_id=None, drive_id=None):
        self.folder_id = folder_id
        self.drive_id = drive_id
        self.files = []
        self.folders = OrderedDict()

        files = get_child_files(folder_id, drive_id=drive_id)
        if len(files):
            for ind, file_info in files.query('~is_folder').iterrows():
                self.files.append(file_info)
            for ind, folder_info in files.query('is_folder').iterrows():
                sub_title = folder_info['title']
                sub_id = folder_info['id']
                self.folders[sub_id] = sub_title
        else:
            logger.warning('Empty folder: {}'.format(folder_id))


def get_child_files(folder_id, drive_id=None):
    """Get dataframe of files in specified folder of specified drive."""
    file_fields = ("files(kind,id,name,webViewLink,webContentLink,iconLink,"
                   "thumbnailLink,createdTime,modifiedTime,"
                   "lastModifyingUser/displayName,mimeType,trashed)")

    from .admin import SERVICE_HANDLES
    collection = SERVICE_HANDLES['files'].files()
    res = collection.list(q="{!r} in parents".format(folder_id),
                          orderBy='modifiedTime desc',
                          pageSize=100,
                          driveId=drive_id,
                          fields=file_fields,
                          corpora='drive',
                          includeItemsFromAllDrives=True,
                          supportsAllDrives=True,
                          ).execute()
    files = pd.DataFrame.from_records(res['files'])  # type: pd.DataFrame
    if len(files):
        logger.info("Files loaded for folder {}: {} rows total".format(folder_id, len(files)))
        # files.lastModifyingUser = files.lastModifyingUser.apply(lambda v: v['displayName'])
        files.createdTime = files.createdTime.apply(parse_timestamp_str)
        files.modifiedTime = files.modifiedTime.apply(parse_timestamp_str)
        files.rename(columns={'webViewLink': 'url_view',
                              'webContentLink': 'url_content',
                              'thumbnailLink': 'thumb',
                              'iconLink': 'icon',
                              'modifiedTime': 'date_modified',
                              'createdTime': 'date_created',
                              'lastModifyingUser': 'last_user',
                              'name': 'title'
                             }, inplace=True)
        file_cols_show = ['title', 'date_modified', 'last_user']
        file_cols_other = ['id', 'mimeType', 'date_created', 'url_view', 'url_content',
                           'icon', 'kind', 'thumb', 'trashed']
        file_columns = file_cols_show + file_cols_other
        files = files.query('~trashed')  # ignore trashed files
        # ignored_columns = [i for i in files.columns if i not in file_columns]
        files = files[[i for i in file_columns if i in files.columns]].copy()

        files['is_folder'] = files.mimeType.apply(lambda v: v.endswith('folder'))
    else:
        logger.warning("No files found for folder {}.".format(folder_id))
    return files


def extract_folders(root_folder_id):
    """Traverse directories to populate all folder objects given a root folder."""
    # via https://stackoverflow.com/questions/28584470/iterating-over-a-growing-set-in-python
    folder_dict = {}  # will hold {id: Folder}
    title_dict = {}  # will hold titles for folder ids

    root = Folder(folder_id=root_folder_id, drive_id=root_folder_id)
    folder_dict['root'] = root
    title_dict['root'] = 'root'
    for i, title in root.folders.items():
        title_dict[i] = title

    seen_ids = set(root.folders)  # sub-folder ids
    active_ids = set(root.folders)

    i = 0
    while active_ids:
        i += 1
        next_active = set()
        for subfolder_id in active_ids:
            subfolder = Folder(folder_id=subfolder_id, drive_id=root_folder_id)
            folder_dict[subfolder_id] = subfolder
            for new_sub_id in subfolder.folders:
                title_dict[new_sub_id] = subfolder.folders[new_sub_id]
                if new_sub_id not in seen_ids:
                    seen_ids.add(new_sub_id)
                    next_active.add(new_sub_id)
        active_ids = next_active
    return folder_dict, title_dict


def file_tree_to_df(root_folder_id, root_title=None):
    """Build dataframe containing all files in directory tree."""
    # GET FOLDER OBJECTS
    folder_dict, title_dict = extract_folders(root_folder_id)
    if root_title is None:
        root_title = 'ROOT'
    title_dict['root'] = root_title

    # BUILD GRAPH FROM FOLDER > SUB-FOLDER RELATIONSHIPS
    edges = []
    for this_id in folder_dict:
        new_edges = [(this_id, key) for key in folder_dict[this_id].folders]
        edges.extend(new_edges)
    graph = nx.DiGraph()
    graph.add_edges_from(edges)

    # BUILD DATAFRAME
    # if graph.number_of_nodes:
    df_list = []
    for folder_id in folder_dict:
        if folder_id == 'root':
            node_path_str, node_path_str_sm = root_title, root_title
        else:
            node_ids = nx.algorithms.shortest_paths.generic.shortest_path(graph, 'root', folder_id)
            node_titles = [title_dict[i] for i in node_ids]
            node_path_str = ' > '.join(node_titles)
            # Get shortened path for display (skip top directory name)
            if len(node_titles) > 1:
                node_path_str_sm = ' > '.join(node_titles[1:])
            else:
                node_path_str_sm = root_title
        files = folder_dict[folder_id].files
        if files:
            df = pd.DataFrame.from_records(files)
            df.insert(0, 'path', node_path_str)
            df['path_show'] = node_path_str_sm
            df_list.append(df)
    if df_list:
        df = pd.concat(df_list, axis=0, ignore_index=True, sort=True)
        df = df[['path'] + [i for i in df.columns if i != 'path']]
    else:
        df = pd.DataFrame()
    return df


def download_raw_file(file_id):
    """Get binary data for file."""
    from .admin import SERVICE_HANDLES
    request = SERVICE_HANDLES['files'].files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))
    return fh


def download_file(file_id, title, mime_orig):
    """Download Drive file, converting format if necessary.

    Args:
        file_id (str): Drive file id.
        title (str): Drive file title.
        mime_orig (str): Mime type of Drive file.
    Returns:
        fh (io.BytesIO): file stream
        filename: file and extension of output file
        mime_out: output mime type
    """
    from .admin import SERVICE_HANDLES
    file_id = file_id

    if mime_orig in MIME_MAP:
        mime_out, extension = MIME_MAP[mime_orig]
        request = SERVICE_HANDLES['files'].files().export_media(fileId=file_id,
                                                                mimeType=mime_out)
        filename = ''.join([title, extension])
    else:  # direct download
        request = SERVICE_HANDLES['files'].files().get_media(fileId=file_id)
        filename = title
        mime_out = mime_orig
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        # print("Download %d%%." % int(status.progress() * 100))
    logger.info('Downloaded {}'.format(title))
    return fh, filename, mime_out


def download_folder_zip(files_df):
    """Combine all files into single zip file stream to send to user.

    Returns:
        zipped_file (io.BytesIO): zip file buffer.
    """
    import io
    import zipfile

    zipped_file = io.BytesIO()
    with zipfile.ZipFile(zipped_file, 'w') as f:
        for ind, r in files_df.iterrows():
            logger.info('Adding to zip: {}'.format(r.title))
            fh, filename, mime_out = download_file(r.id, r.title, r.mimeType)
            f.writestr(filename, fh.getvalue())

    return zipped_file
