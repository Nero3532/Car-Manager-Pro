import os
import sys

def get_app_data_path():
    """Returns the path where the application data (DB, uploads) should be stored.
    For portable mode, this is the directory of the executable or script.
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        return os.path.dirname(sys.executable)
    else:
        # Running from source
        return os.path.dirname(os.path.abspath(__file__))

def get_db_path():
    return os.path.join(get_app_data_path(), 'vehicles.db')

def get_uploads_path():
    path = os.path.join(get_app_data_path(), 'uploads')
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def get_backups_path():
    path = os.path.join(get_app_data_path(), 'backups')
    if not os.path.exists(path):
        os.makedirs(path)
    return path
