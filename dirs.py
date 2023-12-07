import os
import errno
from config import get_config as read_config

config = read_config()
# List of directory paths to create
dirs_to_create = [
    config["v2storagedir"],
    config["v2manifestdir"],
    config["storagedir"],
    config["manifestdir"],
    config["packagedir"],
    "logs",
    "client",
    "files",
    "files/users",
    "files/temp",
    "files/convert",
    "files/cache",
    "client/cafe_server",
]

def create_dirs() :
    # Create directories
    for dir_path in dirs_to_create:
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:  # Ignore if the directory already exists
                raise