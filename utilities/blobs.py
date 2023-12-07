import struct

import utils




class BlobBuilder(object) :
    def __init__(self) :
        self.registry = {}

    def add_entry(self, key, value) :
        if key in self.registry :
            if not isinstance(self.registry[key], list) :
                self.registry[key] = [self.registry[key]]
            self.registry[key].append(value)
        else :
            if not isinstance(value, dict) :
                self.registry[key] = value
            else :
                self.registry[key] = value

    def add_subdict(self, parent_key, subdict_key, subdict) :
        if parent_key in self.registry :
            if not isinstance(self.registry[parent_key], dict) :
                self.registry[parent_key] = {self.registry[parent_key] : None}
            self.registry[parent_key][subdict_key] = subdict
        else :
            self.registry[parent_key] = {
                subdict_key : subdict
            }

    def to_bytes(self, item) :
        if isinstance(item, str) :
            return item
        elif isinstance(item, dict) :
            return {
                self.to_bytes(key) : self.to_bytes(value)
                for key, value in item.items( )
            }
        elif isinstance(item, list) :
            return [self.to_bytes(value) for value in item]
        return item

    def add_entry_as_bytes(self, key, value) :
        self.add_entry(self.to_bytes(key), self.to_bytes(value))


def blob_unserialize(blobtext) :
    if blobtext[0 :2] == b"\x01\x43" :
        # print("decompress")
        blobtext = zlib.decompress(blobtext[20 :])

    blobdict = {}
    (totalsize, slack) = struct.unpack("<LL", blobtext[2 :10])

    if slack :
        blobdict[b"__slack__"] = blobtext[-slack :]
    if (totalsize + slack) != len(blobtext) :
        raise NameError("Blob not correct length including slack space!")
    index = 10
    while index < totalsize :
        namestart = index + 6
        (namesize, datasize) = struct.unpack("<HL", blobtext[index :namestart])
        datastart = namestart + namesize
        name = blobtext[namestart :datastart]
        dataend = datastart + datasize
        data = blobtext[datastart :dataend]
        if len(data) > 1 and data[0 :2] == b"\x01\x50" :
            sub_blob = blob_unserialize(data)
            blobdict[name] = sub_blob
        else :
            blobdict[name] = data
        index = index + 6 + namesize + datasize

    return blobdict


def blob_serialize(blobdict) :
    blobtext = b""

    for (name, data) in blobdict.items( ) :

        if name == b"__slack__" :
            continue

        # Ensure name is a bytes object
        name_bytes = name.encode( ) if isinstance(name, str) else name

        if isinstance(data, dict) :
            data = blob_serialize(data)

        # Ensure data is in bytes format
        if isinstance(data, str) :
            data = data.encode(
                    'utf-8')  # Convert string values to bytes using UTF-8 encoding (or the appropriate encoding)

        namesize = len(name_bytes)
        datasize = len(data)

        subtext = struct.pack("<HL", namesize, datasize)
        subtext = subtext + name_bytes + data
        blobtext = blobtext + subtext

    if b"__slack__" in blobdict :
        slack = blobdict[b"__slack__"]
    else :
        slack = b""

    totalsize = len(blobtext) + 10

    sizetext = struct.pack("<LL", totalsize, len(slack))

    # Convert size text to bytes and concatenate
    blobtext = b'\x01' + b'\x50' + sizetext + blobtext + slack

    return blobtext


def blob_dump(blob, spacer=""):
    text = spacer + "{"
    spacer2 = spacer + "    "
    print(spacer)
    blobkeys = list(blob.keys())
    blobkeys.sort(key=utils.sortkey)
    first = True
    for key in blobkeys:

        data = blob[key]
        if isinstance(data, dict):
            formatted_key = utils.formatstring(key)
            formatted_data = blob_dump(data, spacer2)
        else:
            # Assuming formatstring handles other types appropriately
            formatted_key = utils.formatstring(key)
            formatted_data = utils.formatstring(data)

        if first:

            text += "" + spacer2 + formatted_key + ": " + formatted_data
            first = False
        else:
            text += "," + spacer2 + formatted_key + ": " + formatted_data

    text += spacer + "}"
    return text


def blob_replace(blob_dict, replacement_dict) :
    for (search, replace, info) in replacement_dict :
        fulllength = len(search)
        newlength = len(replace)
        missinglength = fulllength - newlength
        if missinglength < 0 :
            print(
                    "WARNING: Replacement text " + replace.decode( ) + " is too long! Not replaced!")
        else :
            blob_dict = blob_dict.replace(search, replace)
            print(
                    "Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
    return blob_dict


class Application :
    "Empty class that acts as a placeholder"
    pass


def get_apps_list(blob) :
    subblob = blob[b"\x01\x00\x00\x00"]

    apps = {}

    for appblob in subblob :
        app = Application( )
        app.binid = appblob
        app.id = struct.unpack("<L", appblob)[0]
        app.version = struct.unpack("<L", subblob[appblob][b"\x0b\x00\x00\x00"])[0]
        app.size = struct.unpack("<L", subblob[appblob][b"\x05\x00\x00\x00"])[0]
        app.name = subblob[appblob][b"\x02\x00\x00\x00"]

        apps[app.id] = app

    return apps