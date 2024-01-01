

import os
import struct
import sys
import numpy as np

from utilities.encryption import config
from utilities.indexes import readindexes, readindexes_old


class Old_Storage(object):
    def __init__(self, storagename, path, suffix = ""):
        self.name = str(storagename)

        self.indexfile = path + self.name + suffix + ".index"
        self.datafile = path + self.name + suffix + ".data"

        (self.indexes, self.filemodes) = readindexes(self.indexfile)

        self.f = False

    def readchunk(self, fileid, chunkid):
        index = self.indexes[fileid]

        if not self.f:
            self.f = open(self.datafile, "rb")

        pos = chunkid * 16

        (start, length) = struct.unpack(">QQ", index[pos:pos + 16])

        self.f.seek(start)
        file = self.f.read(length)

        return file, self.filemodes[fileid]

    def readchunks(self, fileid, chunkid, maxchunks):

        filechunks = []
        index = self.indexes[fileid]

        if not self.f:
            self.f = open(self.datafile, "rb")

        indexstart = chunkid * 16

        for pos in range(indexstart, len(index), 16):
            (start, length) = struct.unpack(">QQ", index[pos:pos + 16])

            self.f.seek(start)
            filechunks.append(self.f.read(length))

            maxchunks = maxchunks - 1

            if maxchunks == 0:
                break

        return filechunks, self.filemodes[fileid]

    def readfile(self, fileid):

        filechunks = []
        index = self.indexes[fileid]

        if not self.f:
            self.f = open(self.datafile, "rb")

        for pos in range(0, len(index), 16):
            (start, length) = struct.unpack(">QQ", index[pos:pos + 16])

            self.f.seek(start)
            filechunks.append(self.f.read(length))

        return filechunks, self.filemodes[fileid]

    def writefile(self, fileid, filechunks, filemode):

        if fileid in self.indexes:
            print("FileID already exists!")
            sys.exit()

        if self.f:
            self.f.close()
            self.f = False
        f = open(self.datafile, "a+b")
        fi = open(self.indexfile, "ab")

        f.seek(0, 2)  # this is a hack to get the f.tell() to show the correct position

        outindex = struct.pack(">QQQ", fileid, len(filechunks) * 16, filemode)

        for chunk in filechunks:
            outfilepos = f.tell()

            outindex += struct.pack(">QQ", outfilepos, len(chunk))

            f.write(chunk)

        fi.write(outindex)

        f.close()
        fi.close()

        self.indexes[fileid] = outindex[12:]
        self.filemodes[fileid] = filemode

    def close(self):
        if self.f:
            self.f.close()
            self.f = False


class Storage(object):
    def __init__(self, storagename, path, version, islan=False):
        self.name = str(storagename)
        self.ver = str(version)

        if path.endswith("storages/"):
            # manifestpath = path[:-9] + "manifests/"
            manifestpathnew = config["manifestdir"]
            manifestpathold = config["v2manifestdir"]
            manifestpathxtra = config["v3manifestdir2"]
        else:
            return

        if os.path.isfile("files/cache/" + self.name + "_" + self.ver + "/" + self.name + "_" + self.ver + ".manifest"):
            self.indexfile = "files/cache/" + self.name + "_" + self.ver + "/" + self.name + ".index"
            self.datafile = "files/cache/" + self.name + "_" + self.ver + "/" + self.name + ".data"

            (self.indexes, self.filemodes) = readindexes(self.indexfile)
            self.new = True
        elif os.path.isfile(manifestpathold + self.name + "_" + self.ver + ".manifest"):
            self.indexfile = config["v2storagedir"] + self.name + ".index"
            self.datafile = config["v2storagedir"] + self.name + ".data"

            (self.indexes, self.filemodes) = readindexes_old(self.indexfile)
            self.new = False
        elif os.path.isfile(manifestpathxtra + self.name + "_" + self.ver + ".manifest"):
            self.indexfile = config["v3storagedir2"] + self.name + ".index"
            self.datafile = config["v3storagedir2"] + self.name + ".data"

            (self.indexes, self.filemodes) = readindexes(self.indexfile)
            self.new = True
        else:
            self.indexfile = config["storagedir"] + self.name + ".index"
            self.datafile = config["storagedir"] + self.name + ".data"

            (self.indexes, self.filemodes) = readindexes(self.indexfile)
            self.new = True

        self.f = False

    def readchunk(self, fileid, chunkid):
        index = self.indexes[fileid]

        if not self.f:
            self.f = open(self.datafile, "rb")

        pos = chunkid * 16

        (start, length) = struct.unpack(">QQ", index[pos:pos + 16])

        self.f.seek(start)
        file = self.f.read(length)

        return file, self.filemodes[fileid]

    def readchunks(self, fileid, chunkid, maxchunks):

        if self.new:
            filechunks = []
            index = self.indexes[fileid]

            if not self.f:
                self.f = open(self.datafile, "rb")

            indexstart = chunkid * 16

            for pos in range(indexstart, len(index), 16):
                (start, length) = struct.unpack(">QQ", index[pos:pos + 16])

                self.f.seek(start)
                filechunks.append(self.f.read(length))

                maxchunks -= 1

                if maxchunks == 0:
                    break

            return filechunks, self.filemodes[fileid]

        else:
            filechunks = []
            index = self.indexes[fileid]

            f = open(self.datafile, "rb")

            indexstart = chunkid * 8

            for pos in range(indexstart, len(index), 8):
                (start, length) = struct.unpack(">LL", index[pos:pos + 8])

                f.seek(start)
                filechunks.append(f.read(length))

                maxchunks -= 1

                if maxchunks == 0:
                    break

            return filechunks, self.filemodes[fileid]


    def readfile(self, fileid):
        if fileid not in self.indexes:
            print("FileID does not exist!")
            sys.exit()
        with open(self.datafile, "rb") as f:
            start, length = np.frombuffer(self.indexes[fileid], dtype=np.uint64).reshape(-1, 2).T
            filechunks = [f.read(length[i]) for i in range(len(start))]
        return filechunks, self.filemodes[fileid]

    def writefile(self, fileid, filechunks, filemode):
        if fileid in self.indexes:
            print("FileID already exists!")
            sys.exit()
        if os.path.exists(self.datafile):
            os.remove(self.datafile)
        with open(self.datafile, "a+b") as f, open(self.indexfile, "ab") as fi:
            f.seek(0, 2)  # this is a hack to get the f.tell() to show the correct position
            outindex = np.array([fileid, len(filechunks) * 16, filemode], dtype=np.uint64).tobytes()
            for chunk in filechunks:
                outfilepos = f.tell()
                outindex += np.array([outfilepos, len(chunk)], dtype=np.uint64).tobytes()
                f.write(chunk)
            fi.write(outindex)
        self.indexes[fileid] = outindex[12:]
        self.filemodes[fileid] = filemode