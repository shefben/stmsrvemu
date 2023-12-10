from __future__ import print_function

import ast
import binascii
import os
import os.path
import pprint
import shutil
import threading
import zlib
import time
import ipcalc

from Crypto.Hash import SHA

import globalvars
import utilities.blobs
import utilities.encryption

from listmanagers.contentlistmanager import manager
from utilities.manifests import *
from utilities.neuter import neuter
from listmanagers.contentserverlist_utilities import send_removal, send_heartbeat
from utilities.networkhandler import TCPNetworkHandler

cusConnectionCount = 0


class clientupdateserver(TCPNetworkHandler):
    def __init__(self, port, config):
        super(clientupdateserver, self).__init__(config, port)  # Create an instance of NetworkHandler
        if globalvars.public_ip == "0.0.0.0" :
            server_ip = globalvars.server_ip
        else:
            server_ip = globalvars.public_ip
        self.updateserver_info = {
            'wan_ip' : server_ip,
            'lan_ip' : globalvars.server_ip,
            'port': int(port),
            'region': globalvars.cs_region,
            'timestamp': 1623276000
        }

        if not globalvars.aio_server:
            self.thread2 = threading.Thread(target=self.heartbeat_thread)
            self.thread2.daemon = True
            self.thread2.start()
        else:
            manager.add_contentserver_info(server_ip, globalvars.server_ip, int(port), globalvars.cs_region, "", True)

    def heartbeat_thread(self):
        while True:
            send_heartbeat(self.updateserver_info, "", True)
            time.sleep(1800)  # 30 minutes

    def handle_client(self, client_socket, client_address):
        global cusConnectionCount

        log = logging.getLogger("ClientUpdateSRV")

        clientid = str(client_address) + ": "

        log.info(clientid + "Connected to Client Update Server")
        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
            islan = True
        else:
            islan = False
        msg = client_socket.recv(4)

        if len(msg) == 0:
            log.info(clientid + "Got simple handshake. Closing connection.")

        elif msg == b"\x00\x00\x00\x00":  # \x00 for 2003 beta v2 client update
            log.info(clientid + "Package mode entered")
            client_socket.send(b"\x01")
            while True:
                msg = client_socket.recv_withlen()

                if not msg:
                    log.info(clientid + "no message received")
                    break

                command = struct.unpack(">L", msg[:4])[0]

                if command == 2:  # CELLID
                    client_socket.send(b"\x00\x00" + struct.pack('<h', int(globalvars.cellid)))
                    break

                elif command == 3:
                    log.info(clientid + "Exiting package mode")
                    break

                elif command == 0:
                    # Assuming the first 4 bytes are a command, extract it
                    command = struct.unpack(">L", msg[:4])[0]

                    # Find the position of the first non-zero byte after the command
                    filename_start = 4
                    while msg[filename_start] == 0:
                        filename_start += 1
                        if filename_start >= len(msg):
                            raise ValueError("Filename not found in the message")

                    # Extract the filename length (assuming it's one byte)
                    filenamelength = struct.unpack(">B", msg[filename_start:filename_start + 1])[0]

                    # Extract the filename
                    filename_start += 1  # Move past the length byte
                    filename = msg[filename_start:filename_start + filenamelength]

                    if len(msg) != (filenamelength + 16):
                        log.warning(clientid + "There is extra data in the request")

                    log.info(clientid + filename.decode())

                    if filename[-14:] == "_rsa_signature":
                        newfilename = filename[:-14]
                        if self.config["public_ip"] != "0.0.0.0":
                            try:
                                os.mkdir("files/cache/external")
                            except OSError as error:
                                log.debug(clientid + "External pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
                                if not os.path.isfile("files/cache/internal/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + "betav2/" + newfilename.decode(),
                                           "files/cache/internal/" + newfilename.decode(), self.config["server_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/internal/' + newfilename.decode(), 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + "betav2/" + newfilename.decode(),
                                           "files/cache/external/" + newfilename.decode(), self.config["public_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/external/' + newfilename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + newfilename.decode()):
                                neuter(self.config["packagedir"] + "betav2/" + newfilename.decode(),
                                       "files/cache/" + newfilename.decode(), self.config["server_ip"],
                                       self.config["dir_server_port"], islan)
                            f = open('files/cache/' + newfilename.decode(), 'rb')

                        file = f.read()
                        f.close()

                        signature = utilities.encryption.rsa_sign_message(utilities.encryption.network_key, file)

                        reply = struct.pack('>LL', len(signature), len(signature)) + signature

                        client_socket.send(reply)

                    else:
                        if self.config["public_ip"] != "0.0.0.0":
                            try:
                                os.mkdir("files/cache/external")
                            except OSError as error:
                                log.debug(clientid + "External pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
                                if not os.path.isfile("files/cache/internal/" + filename.decode()):
                                    print(filename)
                                    neuter(self.config["packagedir"] + "betav2/" + filename.decode(),
                                           "files/cache/internal/" + filename.decode(), self.config["server_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/internal/' + filename.decode(), 'rb')
                                if not os.path.isfile("files/cache/external/" + filename.decode()):
                                    neuter(self.config["packagedir"] + "betav2/" + filename.decode(),
                                           "files/cache/external/" + filename.decode(), self.config["public_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/external/' + filename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + filename.decode()):
                                neuter(self.config["packagedir"] + "betav2/" + filename.decode(), "files/cache/" + filename.decode(),
                                       self.config["server_ip"], self.config["dir_server_port"], islan)
                            f = open('files/cache/' + filename.decode(), 'rb')

                        file = f.read()
                        f.close()

                        reply = struct.pack('>LL', len(file), len(file))

                        client_socket.send(reply)
                        client_socket.send(file, False)
                        # client_socket.close()
                        # log.info(clientid + "Disconnected from File Server")
                        break

                else:
                    log.warning(clientid + "1 invalid Command")

        elif msg == b"\x00\x00\x00\x02" or msg == b"\x00\x00\x00\x03":
            log.info(clientid + "Package mode entered")
            client_socket.send(b"\x01")
            while True:
                msg = client_socket.recv_withlen()

                if not msg:
                    log.info(clientid + "no message received")
                    break

                command = struct.unpack(">L", msg[:4])[0]

                if command == 2:  # CELLID
                    client_socket.send(b"\x00\x00" + struct.pack('<h', int(self.config["cellid"])))
                    break

                elif command == 3:
                    log.info(clientid + "Exiting package mode")
                    break

                elif command == 0:
                    filename_len_byte = 0
                    for bytein in msg:
                        if bytein == 0:
                            filename_len_byte += 1
                        else:
                            break

                    command = struct.unpack(">L", msg[:4])[0]
                    filenamelength = struct.unpack(">B", msg[filename_len_byte:filename_len_byte + 1])
                    filename = msg[filename_len_byte + 1:filename_len_byte + 1 + filenamelength[0]]
                    # (dummy1, filenamelength) = struct.unpack(">LL", msg[4:12])
                    # filename = msg[12:12+filenamelength]
                    # dummy2 = struct.unpack(">L", msg[12+filenamelength:])[0]

                    if len(msg) != (filenamelength[0] + 16):
                        log.warning(clientid + "There is extra data in the request")

                    if filename[-14:] == b"_rsa_signature":
                        newfilename = filename[:-14]
                        if self.config["public_ip"] != "0.0.0.0":
                            try:
                                os.mkdir("files/cache/external")
                            except OSError as error:
                                log.debug(clientid + "External pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) :
                                if not os.path.isfile("files/cache/internal/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + newfilename.decode(),
                                           "files/cache/internal/" + newfilename.decode(), self.config["server_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/internal/' + newfilename.decode(), 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + newfilename.decode(),
                                           "files/cache/external/" + newfilename.decode(), self.config["public_ip"],
                                           self.config["dir_server_port"], islan)
                                f = open('files/cache/external/' + newfilename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + newfilename.decode()):
                                neuter(self.config["packagedir"] + newfilename.decode(), "files/cache/" + newfilename.decode(),
                                       self.config["server_ip"], self.config["dir_server_port"], islan)
                            f = open('files/cache/' + newfilename.decode(), 'rb')

                        file = f.read()
                        f.close()

                        signature = utilities.encryption.rsa_sign_message(utilities.encryption.network_key, file)

                        reply = struct.pack('>LL', len(signature), len(signature)) + signature

                        client_socket.send(reply)

                    else:

                        if self.config["public_ip"] != "0.0.0.0":
                            try:
                                os.mkdir("files/cache/external")
                            except OSError as error:
                                log.debug(clientid + "External pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) :
                                if not os.path.isfile("files/cache/internal/" + filename.decode()):
                                    neuter(self.config["packagedir"] + filename.decode(), "files/cache/internal/" + filename.decode(),
                                           self.config["server_ip"], self.config["dir_server_port"], islan)
                                f = open('files/cache/internal/' + filename.decode(), 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + filename.decode()):
                                    neuter(self.config["packagedir"] + filename.decode(), "files/cache/external/" + filename.decode(),
                                           self.config["public_ip"], self.config["dir_server_port"], islan)
                                f = open('files/cache/external/' + filename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + filename.decode()):
                                neuter(self.config["packagedir"] + filename.decode(), "files/cache/" + filename.decode(),
                                       self.config["server_ip"], self.config["dir_server_port"], islan)
                            f = open('files/cache/' + filename.decode(), 'rb')

                        file = f.read()
                        f.close()

                        reply = struct.pack('>LL', len(file), len(file))

                        client_socket.send(reply)
                        # client_socket.send(file, False)

                        for i in range(0, len(file), 0x500):
                            chunk = file[i:i + 0x500]
                            client_socket.send(chunk, False)

                else:
                    log.warning(clientid + "2 Invalid Command: " + str(command))

        elif msg == b"\x00\x00\x00\x07":
            log.info(clientid + "CDDB mode entered")
            client_socket.send(b"\x01")
            while True:
                msg = client_socket.recv_withlen()

                if not msg:
                    log.info(clientid + "no message received")
                    break

                if len(msg) == 10:
                    client_socket.send(b"\x01")
                    break

                command = struct.unpack(">B", msg[:1])[0]

                if command == 2:  # SEND CDR

                    if os.path.isfile("files/cache/secondblob.bin"):
                        with open("files/cache/secondblob.bin", "rb") as f:
                            blob = f.read()
                    elif os.path.isfile("files/2ndcdr.py") or os.path.isfile("files/secondblob.py"):
                        if os.path.isfile("files/2ndcdr.orig"):
                            # shutil.copy2("files/2ndcdr.py","files/2ndcdr.orig")
                            os.remove("files/2ndcdr.py")
                            shutil.copy2("files/2ndcdr.orig", "files/secondblob.py")
                            os.remove("files/2ndcdr.orig")
                        if os.path.isfile("files/2ndcdr.py"):
                            shutil.copy2("files/2ndcdr.py", "files/secondblob.py")
                            os.remove("files/2ndcdr.py")
                        with open("files/secondblob.py", "r") as g:
                            file = g.read()

                        for (search, replace, info) in globalvars.replacestringsCDR:
                            print(search)
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print("WARNING: Replacement text " + replace.decode() + " is too long! Not replaced!")
                            else:
                                fileold = file
                                file = file.replace(search, replace)
                                if (search in fileold) and (replace in file):
                                    print("Replaced " + info.decode() + " " + search.decode() + " with " + replace.decode())
                        # h = open("files/2ndcdr.py", "w")
                        # h.write(file)
                        # h.close()

                        execdict = {}
                        execdict_temp_01 = {}
                        execdict_temp_02 = {}
                        # execfile("files/2ndcdr.py", execdict)
                        exec (file, execdict)

                        for file in os.walk("files/custom"):
                            for pyblobfile in file[2]:
                                if (pyblobfile.endswith(".py") or pyblobfile.endswith(
                                        ".bin")) and not pyblobfile == "2ndcdr.py" and not pyblobfile == "1stcdr.py" and not pyblobfile.startswith(
                                        "firstblob") and not pyblobfile.startswith("secondblob"):
                                    # if os.path.isfile("files/extrablob.py") :
                                    log.info(clientid + "Found extra blob: " + pyblobfile)
                                    execdict_update = {}

                                    if pyblobfile.endswith(".bin"):
                                        f = open("files/custom/" + pyblobfile, "rb")
                                        blob = f.read()
                                        f.close()

                                        if blob[0:2] == b"\x01\x43":
                                            blob = zlib.decompress(blob[20:])
                                        blob2 = utilities.blobs.blob_unserialize(blob)
                                        blob3 = utilities.blobs.blob_dump(blob2)
                                        execdict_update = "blob = " + blob3

                                    elif pyblobfile.endswith(".py"):
                                        with open("files/custom/" + pyblobfile, 'r') as m:
                                            userblobstr_upd = m.read()
                                        execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

                                    for k in execdict_update:
                                        for j in execdict["blob"]:
                                            if j == k:
                                                execdict["blob"][j].update(execdict_update[k])
                                            else:
                                                if k == b"\x01\x00\x00\x00":
                                                    execdict_temp_01.update(execdict_update[k])
                                                elif k == b"\x02\x00\x00\x00":
                                                    execdict_temp_02.update(execdict_update[k])

                                    for k, v in execdict_temp_01.items():
                                        execdict["blob"].pop(k, v)

                                    for k, v in execdict_temp_02.items():
                                        execdict["blob"].pop(k, v)

                        blob = utilities.blobs.blob_serialize(execdict["blob"])

                        if blob[0:2] == b"\x01\x43":
                            blob = zlib.decompress(blob[20:])

                        start_search = 0
                        while True:
                            found = blob.find(b"\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
                            if found < 0:
                                break

                            # TINserver's Net Key
                            # BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + b"\x02\x01\x11"

                            # BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + b"\x02\x01\x11"
                            BERstring = binascii.a2b_hex(
                                "30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(
                                self.config["net_key_n"][2:]) + b"\x02\x01\x11"
                            foundstring = blob[found:found + 160]
                            blob = blob.replace(foundstring, BERstring)
                            start_search = found + 160

                        compressed_blob = zlib.compress(blob, 9)
                        blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob),
                                                        9) + compressed_blob

                        # cache_option = self.config["use_cached_blob"]
                        # if cache_option == "true" :
                        f = open("files/cache/secondblob.bin", "wb")
                        f.write(blob)
                        f.close()

                    else:
                        if os.path.isfile("files/secondblob.orig"):
                            os.remove("files/secondblob.bin")
                            shutil.copy2("files/secondblob.orig", "files/secondblob.bin")
                            os.remove("files/secondblob.orig")
                        with open("files/secondblob.bin", "rb") as g:
                            blob = g.read()

                        if blob[0:2] == b"\x01\x43":
                            blob = zlib.decompress(blob[20:])
                        blob2 = utilities.blobs.blob_unserialize(blob)
                        blob3 = utilities.blobs.blob_dump(blob2)
                        file = "blob = " + blob3

                        for (search, replace, info) in globalvars.replacestringsCDR:
                            print("Fixing CDR")
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0:
                                print("WARNING: Replacement text " + replace.decode() + " is too long! Not replaced!")
                            else:
                                file = file.replace(search, replace)
                                print("Replaced " + info.decode() + " " + search.decode() + " with " + replace.decode())

                        execdict = {}
                        execdict_temp_01 = {}
                        execdict_temp_02 = {}
                        exec (file, execdict)

                        for file in os.walk("files/custom"):
                            for pyblobfile in file[2]:
                                if (pyblobfile.endswith(".py") or pyblobfile.endswith(
                                        ".bin")) and not pyblobfile == "2ndcdr.py" and not pyblobfile == "1stcdr.py" and not pyblobfile.startswith(
                                        "firstblob") and not pyblobfile.startswith("secondblob"):
                                    # if os.path.isfile("files/extrablob.py") :
                                    log.info(clientid + "Found extra blob: " + pyblobfile)
                                    execdict_update = {}

                                    if pyblobfile.endswith(".bin"):
                                        f = open("files/custom/" + pyblobfile, "rb")
                                        blob = f.read()
                                        f.close()

                                        if blob[0:2] == b"\x01\x43":
                                            blob = zlib.decompress(blob[20:])
                                        blob2 = utilities.blobs.blob_unserialize(blob)
                                        blob3 = utilities.blobs.blob_dump(blob2)
                                        execdict_update = "blob = " + blob3

                                    elif pyblobfile.endswith(".py"):
                                        with open("files/custom/" + pyblobfile, 'r') as m:
                                            userblobstr_upd = m.read()
                                        execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])

                                    for k in execdict_update:
                                        for j in execdict["blob"]:
                                            if j == k:
                                                execdict["blob"][j].update(execdict_update[k])
                                            else:
                                                if k == b"\x01\x00\x00\x00":
                                                    execdict_temp_01.update(execdict_update[k])
                                                elif k == b"\x02\x00\x00\x00":
                                                    execdict_temp_02.update(execdict_update[k])

                                    for k, v in execdict_temp_01.items():
                                        execdict["blob"].pop(k, v)

                                    for k, v in execdict_temp_02.items():
                                        execdict["blob"].pop(k, v)

                        blob = utilities.blobs.blob_serialize(execdict["blob"])

                        # h = open("files/secondblob.bin", "wb")
                        # h.write(blob)
                        # h.close()

                        # g = open("files/secondblob.bin", "rb")
                        # blob = g.read()
                        # g.close()

                        if blob[0:2] == b"\x01\x43":
                            blob = zlib.decompress(blob[20:])

                        start_search = 0
                        while True:
                            found = blob.find(b"\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
                            if found < 0:
                                break

                            # TINserver's Net Key
                            # BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + b"\x02\x01\x11"

                            # BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + b"\x02\x01\x11"
                            BERstring = binascii.a2b_hex(
                                "30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(
                                self.config["net_key_n"][2:]) + b"\x02\x01\x11"
                            foundstring = blob[found:found + 160]
                            blob = blob.replace(foundstring, BERstring)
                            start_search = found + 160

                        compressed_blob = zlib.compress(blob, 9)
                        blob = b"\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob),
                                                        9) + compressed_blob

                        # cache_option = self.config["use_cached_blob"]
                        # if cache_option == "true" :
                        f = open("files/cache/secondblob.bin", "wb")
                        f.write(blob)
                        f.close()

                    checksum = SHA.new(blob).digest()

                    if checksum == msg[1:]:
                        log.info(clientid + "Client has matching checksum for secondblob")
                        log.debug(clientid + "We validate it: " + binascii.b2a_hex(msg[1:]).decode())

                        client_socket.send(b"\x00\x00\x00\x00")

                    else:
                        log.info(clientid + "Client didn't match our checksum for secondblob")
                        log.debug(clientid + "Sending new blob: " + binascii.b2a_hex(msg[1:]).decode())

                        client_socket.send_withlen(blob, False)

                else:
                    log.warning(clientid + "Unknown command: " + str(msg[0:1]))
        else:
            log.warning("3 Invalid Command: " + binascii.b2a_hex(msg).decode())

        client_socket.close()
        log.info(clientid + "Disconnected from Client Update Server")