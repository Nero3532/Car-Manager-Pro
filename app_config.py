import os
import sys
from path_utils import get_writable_path

def get_app_data_path():
    """Returns the path where the application data (DB, uploads) should be stored.
    For portable mode, this is the directory of the executable or script.
    """
    return get_writable_path("")

def get_db_path():
    return get_writable_path('vehicles.db')

def get_uploads_path():
    path = get_writable_path('uploads')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_backups_path():
    path = get_writable_path('backups')
    if not os.path.exists(path):
        os.makedirs(path)
    return path
