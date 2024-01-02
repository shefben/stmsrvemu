

import logging
import os
import sys
import time
import zlib

import config
import globalvars

from utilities import storages
from utilities.checksums import Checksums
from utilities.gcf import GCF

config = config.read_config()


def create_progress_bar(total, filename):
    if config["show_convert_bar"].lower() == "true":
        try:
            from tqdm import tqdm
            print("Converting File: " + filename)
            return tqdm(total=total, unit="file", dynamic_ncols=False)
        except ImportError:
            pass
    # Return None when show_convert_bar is false
    return None


def compare_checksums(less, more):
    for fileid in range(less.numfiles):
        if less.checksums_raw[fileid] != more.checksums_raw[fileid]:
            print(f"Checksums doesn't match for file {fileid} {len(less.checksums_raw[fileid])} {len(more.checksums_raw[fileid])}")
            sys.exit()


def gcf2storage(filename):
    log = logging.getLogger("converter")

    is_wan_file = filename.endswith("_wan.neutered.gcf")
    is_lan_file = filename.endswith("_lan.neutered.gcf")
    file_suffix = "_wan" if is_wan_file else "_lan" if is_lan_file else ""

    do_updates = True
    gcf = GCF(filename)

    progress_bar = create_progress_bar(len(gcf.manifest.dir_entries), filename)
    manifestdir = "files/cache/" + str(gcf.appid) + "_" + str(gcf.appversion) + "/"
    storagedir = "files/cache/" + str(gcf.appid) + "_" + str(gcf.appversion) + "/"

    if not os.path.isdir(manifestdir):
        os.makedirs(manifestdir, exist_ok=True)

    storage = storages.Old_Storage(gcf.appid, storagedir, file_suffix)

    manifest_filename = os.path.join(manifestdir, f"{gcf.appid}_{gcf.appversion}.manifest")

    if os.path.isfile(manifest_filename):
        f = open(manifest_filename, "rb")
        stored_manifest_data = f.read()
        f.close()

        if stored_manifest_data != gcf.manifest_data:
            print("Manifests differ!!")
            sys.exit()
        #else:
        #    print("Manifests match, continuing..")
    else:
        # print "New manifest"

        # we write a new manifest anyway
        f = open(manifest_filename, "wb")
        f.write(gcf.manifest_data)
        f.close()

    gcf_checksums = Checksums(gcf.checksum_data)

    checksum_filename = os.path.join(storagedir, f"{gcf.appid}{file_suffix}.checksums")
    if os.path.isfile(checksum_filename):
        stored_checksums = Checksums()
        stored_checksums.load_from_file(checksum_filename)

        if gcf_checksums.numfiles > stored_checksums.numfiles:
            print("Checksums in GCF have more files than checksums in storage")
            compare_checksums(stored_checksums, gcf_checksums)

            if do_updates:
                timex = str(int(time.time()))
                os.rename(checksum_filename, checksum_filename + "." + timex + ".bak")
                f = open(checksum_filename, "wb")
                f.write(gcf.checksum_data)
                f.close()
        else:
            print("Checksums in storage have equal or more files than checksums in GCF")
            compare_checksums(gcf_checksums, stored_checksums)
    else:
        if do_updates:
            f = open(checksum_filename, "wb")
            f.write(gcf.checksum_data)
            f.close()

    # print "Checking files "

    for (dirid, d) in gcf.manifest.dir_entries.items():

        if progress_bar:
            progress_bar.update(1)  # Increment the progress bar

        if d.fileid == 0xffffffff:
            continue

        if gcf_checksums.numchecksums[d.fileid] == 0:
            continue

        if d.dirtype & 0x100:
            print(f"File encrypted {d.fileid}")
            continue
        if d.fileid not in storage.indexes:
            # print "File not in storage", d.fileid, d.fullfilename

            if d.dirtype & 0x100:
                file = []
                for gcf_block in gcf.get_file(dirid):
                    file.append(gcf_block)
                file = b"".join(file)
                # print binascii.b2a_hex(file[:64])

            else:
                if do_updates:
                    file = []
                    for gcf_block in gcf.get_file(dirid):
                        file.append(gcf_block)
                    file = b"".join(file)

                    if len(file) != d.itemsize:
                        print(f"Length of extracted file and file size doesn't match! {len(file)} {d.itemsize}")
                        sys.exit()

                    chunks = []
                    chunkid = 0
                    for start in range(0, len(file), 32768):
                        chunk = file[start:start + 32768]

                        if not gcf_checksums.validate_chunk(d.fileid, chunkid, chunk, checksum_filename):
                            # print "Checksum failed!"
                            # failed = "1"
                            log.debug("Checksum fixed!")
                            # sys.exit()

                        chunks.append(zlib.compress(chunk, 9))
                        chunkid += 1

                    # print "Writing file to storage", d.fullfilename, len(file)
                    storage.writefile(d.fileid, chunks, 1)
                    continue
        else:
            if storage.filemodes[d.fileid] == 2 or storage.filemodes[d.fileid] == 3:
                print(f"File is encrypted in storage but not in GCF {d.fileid}")
                sys.exit()

            storage_chunk = b""
            storage_chunkid = 0
            gcf_chunk = b""
            totalsize = 0
            for gcf_block in gcf.get_file(dirid):
                if not storage_chunk:
                    (storage_chunk, filemode) = storage.readchunk(d.fileid, storage_chunkid)
                    if len(storage_chunk):
                        storage_chunk = zlib.decompress(storage_chunk)

                gcf_chunk += gcf_block
                totalsize += len(gcf_block)
                if len(gcf_chunk) >= len(storage_chunk):
                    if gcf_chunk != storage_chunk:
                        print(f"Difference between chunks!!! {len(gcf_chunk)} {len(storage_chunk)}")
                        sys.exit()
                    else:
                        # print "\b.",
                        pass

                    storage_chunk = b""
                    storage_chunkid += 1
                    gcf_chunk = b""

            # print storage_chunkid, gcf_checksums.numchecksums[d.fileid]

            if totalsize != d.itemsize:
                print("")
                print(f"Different sizes, file incomplete? {d.fileid} {totalsize} {d.itemsize}")
                # sys.exit()
            else:
                print("\b.", end=' ')

        if progress_bar:
            progress_bar.close()  # Close the progress bar when don
            globalvars.hide_convert_prints = False

if __name__ == "__main__":
    gcf2storage(sys.argv[1])