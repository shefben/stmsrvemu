import ast
import binascii
import os
import os.path
import shutil
import threading
import time
import zlib

import ipcalc
from Crypto.Hash import SHA

import globalvars
import utilities.blobs
import utilities.encryption
from listmanagers.contentlistmanager import manager
from listmanagers.contentserverlist_utilities import send_heartbeat
from utilities import cdr_manipulator
from utilities.manifests import *
from utilities.networkhandler import TCPNetworkHandler
from utilities.neuter import neuter

cusConnectionCount = 0


class clientupdateserver(TCPNetworkHandler):
    def __init__(self, port, config):
        super(clientupdateserver, self).__init__(config, port)  # Create an instance of NetworkHandler
        if globalvars.public_ip == "0.0.0.0":
            server_ip = globalvars.server_ip
        else:
            server_ip = globalvars.public_ip
        self.updateserver_info = {'wan_ip':server_ip, 'lan_ip':globalvars.server_ip, 'port':int(port), 'region':globalvars.cs_region, 'timestamp':1623276000}

        if not globalvars.aio_server:
            self.thread2 = threading.Thread(target = self.heartbeat_thread)
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
        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) or globalvars.public_ip == str(client_address[0]):
            islan = True
        else:
            islan = False
        msg = client_socket.recv(4)

        if len(msg) == 0:
            log.info(clientid + "Got simple handshake. Closing connection.")

        elif msg == b"\x00\x00\x00\x00":  # 2003 beta v2 client update
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
                        log.warning(f"{clientid}There is extra data in the request packet: {msg}")

                    log.info(clientid + filename.decode())

                    if filename[-14:] == "_rsa_signature":
                        newfilename = filename[:-14]
                        if self.config["public_ip"] != "0.0.0.0":
                            try:
                                os.mkdir("files/cache/external")
                            except OSError as error:
                                log.debug(clientid + "External beta pkg dir already exists")
                            try:
                                os.mkdir("files/cache/external/betav2")
                            except OSError as error:
                                log.debug(clientid + "External beta pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal beta pkg dir already exists")
                            try:
                                os.mkdir("files/cache/internal/betav2")
                            except OSError as error:
                                log.debug(clientid + "Internal beta pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) or globalvars.public_ip == str(client_address[0]):
                                if not os.path.isfile("files/cache/internal/betav2/" + newfilename):
                                    neuter(self.config["packagedir"] + "betav2/" + newfilename, "files/cache/internal/betav2/" + newfilename, self.config["server_ip"], self.config["dir_server_port"], True)
                                f = open('files/cache/internal/betav2/' + newfilename, 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/betav2/" + newfilename):
                                    neuter(self.config["packagedir"] + "betav2/" + newfilename, "files/cache/external/betav2/" + newfilename, self.config["public_ip"], self.config["dir_server_port"], False)
                                f = open('files/cache/external/betav2/' + newfilename, 'rb')
                        else:
                            try:
                                os.mkdir("files/cache/betav2")
                            except OSError as error:
                                log.debug(clientid + "Beta pkg dir already exists")
                            if not os.path.isfile("files/cache/betav2/" + newfilename):
                                neuter(self.config["packagedir"] + "betav2/" + newfilename, "files/cache/betav2/" + newfilename, self.config["server_ip"], self.config["dir_server_port"], True)
                            f = open('files/cache/betav2/' + newfilename, 'rb')

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
                                os.mkdir("files/cache/external/betav2")
                            except OSError as error:
                                log.debug(clientid + "External beta pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal")
                            except OSError as error:
                                log.debug(clientid + "Internal pkg dir already exists")

                            try:
                                os.mkdir("files/cache/internal/betav2")
                            except OSError as error:
                                log.debug(clientid + "Internal beta pkg dir already exists")

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) or globalvars.public_ip == str(client_address[0]):
                                if not os.path.isfile("files/cache/internal/betav2/" + filename):
                                    neuter(self.config["packagedir"] + "betav2/" + filename, "files/cache/internal/betav2/" + filename, self.config["server_ip"], self.config["dir_server_port"], True)
                                f = open('files/cache/internal/betav2/' + filename, 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + filename.decode()):
                                    if not os.path.isfile("files/cache/external/betav2/" + filename):
                                        neuter(self.config["packagedir"] + "betav2/" + filename, "files/cache/external/betav2/" + filename, self.config["public_ip"], self.config["dir_server_port"], False)
                                    f = open('files/cache/external/betav2/' + filename, 'rb')
                        else:
                            try:
                                os.mkdir("files/cache/betav2")
                            except OSError as error:
                                log.debug(clientid + "Beta pkg dir already exists")
                            if not os.path.isfile("files/cache/betav2/" + filename):
                                neuter(self.config["packagedir"] + "betav2/" + filename, "files/cache/betav2/" + filename, self.config["server_ip"], self.config["dir_server_port"], True)
                            f = open('files/cache/betav2/' + filename, 'rb')

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

        elif msg == b"\x00\x00\x00\x02" or msg == b"\x00\x00\x00\x03":  # release client update
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

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) or globalvars.public_ip == str(client_address[0]) or islan:
                                if not os.path.isfile("files/cache/internal/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + newfilename.decode(), "files/cache/internal/" + newfilename.decode(), self.config["server_ip"], self.config["dir_server_port"], True)
                                f = open('files/cache/internal/' + newfilename.decode(), 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + newfilename.decode()):
                                    neuter(self.config["packagedir"] + newfilename.decode(), "files/cache/external/" + newfilename.decode(), self.config["public_ip"], self.config["dir_server_port"], False)
                                f = open('files/cache/external/' + newfilename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + newfilename.decode()):
                                neuter(self.config["packagedir"] + newfilename.decode(), "files/cache/" + newfilename.decode(), self.config["server_ip"], self.config["dir_server_port"], True)
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

                            if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) or globalvars.public_ip == str(client_address[0]) or islan:
                                if not os.path.isfile("files/cache/internal/" + filename.decode()):
                                    neuter(self.config["packagedir"] + filename.decode(), "files/cache/internal/" + filename.decode(), self.config["server_ip"], self.config["dir_server_port"], True)
                                f = open('files/cache/internal/' + filename.decode(), 'rb')
                            else:
                                if not os.path.isfile("files/cache/external/" + filename.decode()):
                                    neuter(self.config["packagedir"] + filename.decode(), "files/cache/external/" + filename.decode(), self.config["public_ip"], self.config["dir_server_port"], False)
                                f = open('files/cache/external/' + filename.decode(), 'rb')
                        else:
                            if not os.path.isfile("files/cache/" + filename.decode()):
                                neuter(self.config["packagedir"] + filename.decode(), "files/cache/" + filename.decode(), self.config["server_ip"], self.config["dir_server_port"], True)
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

        elif msg == b"\x00\x00\x00\x07":  # cdr download
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

                    blob = cdr_manipulator.fixblobs(islan)  # self.clupdate_modify_blob(clientid, log, islan)

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