import binascii
import logging
import socket
import struct
import time

import ipcalc
from Crypto.Hash import SHA

import globalvars
import utils
from utilities import cdr_manipulator, encryption
from utilities.database import ccdb
from utilities.networkhandler import TCPNetworkHandler


class configserver(TCPNetworkHandler):
    def __init__(self, port, config):
        self.server_type = "ConfigServer"
        # Create an instance of NetworkHandler
        super(configserver, self).__init__(config, port, self.server_type)

    def handle_client(self, client_socket, client_address):
        log = logging.getLogger(self.server_type)

        # Load this everytime a client connects, this ensures that we can change the blob without restarting the server
        firstblob = ccdb.load_ccdb( )

        clientid = str(client_address) + ": "

        log.info(clientid + "Connected to Config Server")
        valid_version = 0
        command = client_socket.recv(4)
        if command == b"\x00\x00\x00\x02" or command == b"\x00\x00\x00\x00":  # \x02 for steam_0
            client_socket.send(b"\x01")
            valid_version = 1
        elif command == b"\x00\x00\x00\x03":
            client_socket.send(b"\x01" + socket.inet_aton(client_address[0]))
            valid_version = 1
        else:
            log.info(clientid + "Invalid head message: " + binascii.b2a_hex(command).decode())
            valid_version = 0

        if valid_version == 1:
            command = client_socket.recv_withlen()

            if len(command) == 1:

                if command == b"\x01" :  # send ccdb
                    log.info(clientid + "sending first blob")

                    if globalvars.steamui_ver < 61:  # guessing steamui version when steam client interface v2 changed to v3
                        globalvars.tgt_version = "1"
                        log.debug(clientid + "TGT version set to 1")
                    else:
                        globalvars.tgt_version = "2"  # config file states 2 as default
                        log.debug(clientid + "TGT version set to 2")
                    client_socket.send_withlen(firstblob)

                elif command == b"\x04" :  # send net key
                    log.info(clientid + "sending network key")
                    # This is cheating. I've just cut'n'pasted the hex from the network_key. FIXME
                    client_socket.send(encryption.signed_mainkey_reply)

                elif command == b"\x05":
                    log.info(clientid + "confserver command 5, GetCurrentAuthFailSafeMode, sending zero reply")
                    client_socket.send(b"\x00")

                elif command == b"\x06":
                    log.info(clientid + "confserver command 6, GetCurrentBillingFailSafeMode, sending zero reply")
                    client_socket.send(b"\x00")

                elif command == b"\x07":
                    log.info(clientid + "Sending out list of Content Servers / GetCurrentContentFailSafeMode")

                    # client_socket.send(binascii.a2b_hex("0001312d000000012c"))
                    # TODO Grab IP from Directory Server
                    if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
                        bin_ip = utils.encodeIP((self.config["server_ip"], self.config["content_server_port"]))
                    else:
                        bin_ip = utils.encodeIP((self.config["public_ip"], self.config["content_server_port"]))

                    reply = struct.pack(">H", 1) + bin_ip

                    client_socket.send_withlen(reply)

                elif command == b"\x08":
                    log.info(clientid + "confserver command 8, GetCurrentSteam3LogonPercent, sending zero reply")
                    client_socket.send(b"\x00\x00\x00\x00")

                else:
                    log.warning(clientid + "Invalid command: " + binascii.b2a_hex(command).decode())
                    client_socket.send(b"\x00")

            elif command[0:1] == b"\x02" or command[0:1] == b"\x09":  # send cddb

                if command[0:1] == b"\x09":
                    client_socket.send(binascii.a2b_hex("00000001312d000000012c"))

                while globalvars.compiling_cdr:
                    time.sleep(1)

                blob = cdr_manipulator.fixblobs_configserver()
                checksum = SHA.new(blob).digest()

                if checksum == command[1:]:
                    log.info(clientid + "Client has matching checksum for secondblob")
                    log.debug(clientid + "We validate it: " + binascii.b2a_hex(command).decode())
                    client_socket.send(b"\x00\x00\x00\x00")

                else:
                    log.info(clientid + "Client didn't match our checksum for secondblob")
                    log.debug(clientid + "Sending new blob: " + binascii.b2a_hex(command).decode())

                    client_socket.send_withlen(blob, True)  # false for not showing in log

            else:
                log.info(clientid + "Invalid message: " + binascii.b2a_hex(command).decode())

        client_socket.close()

        log.info(clientid + "disconnected from Config Server")