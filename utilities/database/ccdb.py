import ast
import os
import pprint
import shutil
import struct
import logging
import sys
import zlib
import logging

from config import get_config
from utilities.database import dbengine  # Import the function to create database driver
from utilities import blobs, packages

log = logging.getLogger("CCDB")

config = get_config()

def process_date(date_str):
    for char in [":", "/", "\\", "-", "_"]:
        date_str = date_str.replace(char, "")
    print(date_str)
    return date_str


def process_time(time_str):
    time = time_str.replace(":", "")
    print(time)
    return time


def create_firstblob_from_row(row):
    firstblob = {}

    columns_with_null = [8, 10, 12, 14]  # columns that require a null character '\x00' appended to their value

    for i in range(1, 19):
        if row[i] != "":
            key = struct.pack("<L", i - 1)  # Column 1 is key 0, Column 2 is key 1, and so on
            if i in columns_with_null:
                # Append \x00 for columns_with_null
                value = str(row[i]) + "\x00"
            else:
                # Handle as integer for other columns
                value = struct.pack("<L", int(row[i])) if i <= 13 else row[i]
            firstblob[key] = value
    return firstblob


def load_filesys_blob():
    if os.path.isfile("files/1stcdr.py") or os.path.isfile("files/firstblob.py") :
        if os.path.isfile("files/1stcdr.py") :
            shutil.copy2("files/1stcdr.py", "files/firstblob.py")
            os.remove("files/1stcdr.py")
        with open("files/firstblob.py", "r") as f :
            firstblob = f.read( )
        execdict = {}
        # execfile("files/1stcdr.py", execdict)
        exec(firstblob, execdict)
        return blobs.blob_serialize(execdict["blob"]), firstblob
        # firstblob_unser = utils.blob_unserialize(blob)
        # firstblob_bin = utils.blob_serialize(firstblob_unser)
    else :
        with open("files/firstblob.bin", "rb") as f :
            blob = f.read( )
        if blob[0:2] == b"\x01\x43" :
            blob = zlib.decompress(blob[20 :])
        firstblob_unser = blobs.blob_unserialize(blob)
        firstblob = "blob = " + blobs.blob_dump(firstblob_unser)

    return ast.literal_eval(firstblob[7 :len(firstblob)]), blob
def load_ccdb():
    import globalvars
    # Initialize the database driver
    db_driver = dbengine.create_database_driver(globalvars.db_type)
    db_driver.connect()
    if globalvars.use_file_blobs != "true" and str(config["steam_date"]) != "" and str(config["steam_time"]) != "":
        if db_driver.check_table_exists('firstblob'):
            logging.debug("Reading CCDB")

            client_date = process_date(config["steam_date"])
            client_time = process_time(config["steam_time"])

            status = "none"
            firstblob = {}

            while status != "ok":
                query = f"SELECT * FROM firstblob WHERE ccr_blobdate <= '{client_date}' ORDER BY filename DESC"
                rows = db_driver.execute_query(query)
                #print(repr(rows))

                row_num = 0
                if len(rows) > 0 and rows[row_num][20] > client_time and rows[row_num][19] > client_date:
                    row_num = 1
                    log.debug("Defaulting to 2003/01/19 blob")
                if len(rows) == 0:
                    query = f"SELECT * FROM firstblob WHERE ccr_blobdate >= '{client_date}'"
                    rows = db_driver.execute_query(query)

                firstblob = create_firstblob_from_row(rows[0])
                pkg_check_result = packages.check_pkgs(rows[0])
                client_date = str(int(rows[0][19]) - 1)
                client_time = str(int(rows[0][20]) - 1)

                log.debug(f"Package set check result: {pkg_check_result}")
                if pkg_check_result in ["missing", "failed"]:
                    log.warning(f"Requested package set is {pkg_check_result}, trying earlier set...")

                if client_date == "20030119":  # First blob reached
                    logging.error("No more packages available, trying blob files instead.")
                    return load_filesys_blob()  # load .py or .bin blob if DB not found

                status = pkg_check_result

            log.info("Package set validated successfully")
            globalvars.record_ver = struct.unpack("<L", firstblob[b"\x00\x00\x00\x00"])[0]
            globalvars.steam_ver = struct.unpack("<L", firstblob[b"\x01\x00\x00\x00"])[0]
            globalvars.steamui_ver = struct.unpack("<L", firstblob[b"\x02\x00\x00\x00"])[0]
            return blobs.blob_serialize(firstblob)

    log.debug("Using Filesystem firstblobs")
    firstblob, blob = load_filesys_blob()
    globalvars.record_ver = struct.unpack("<L", firstblob[b"\x00\x00\x00\x00"])[0]
    globalvars.steam_ver = struct.unpack("<L", firstblob[b"\x01\x00\x00\x00"])[0]
    globalvars.steamui_ver = struct.unpack("<L", firstblob[b"\x02\x00\x00\x00"])[0]
    return blob  # load .py or .bin blob if DB not found