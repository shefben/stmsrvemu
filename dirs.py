import os
import errno
from config import get_config

config = get_config()

# List of directory paths to create
dirs_to_create = [
    config["v3storagedir2"],
    config["v3manifestdir2"],
    config["v2storagedir"],
    config["v2manifestdir"],
    config["storagedir"],
    config["manifestdir"],
    config["betastoragedir"],
    config["betamanifestdir"],
    config["packagedir"],
    "logs",
    "client",
    "clientstats",
    "clientstats/clientstats",
    "clientstats/gamestats",
    "clientstats/bugreports",
    "clientstats/steamstats",
    "clientstats/phonehome",
    "clientstats/exceptionlogs",
    "clientstats/crashdump",
    "clientstats/surveys",
    "clientstats/downloadstats",
    "files",
    "files/users",
    "files/temp",
    "files/convert",
    "files/cache",
    "files/beta1_ftp",
]

def create_dirs() :
    # Create directories
    for dir_path in dirs_to_create:
        try:
            os.makedirs(dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:  # Ignore if the directory already exists
                raise