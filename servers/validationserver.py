import ast
import binascii
import logging
import os.path
#import socket
import struct
import time
import socket as real_socket

import utilities.encryption
import utils
from utilities import encryption
from utilities.networkhandler import TCPNetworkHandler


class validationserver(TCPNetworkHandler):

    def __init__(self, port, config):
        self.server_type = "ValidationSRV"
        super(validationserver, self).__init__(config, port, self.server_type)  # Create an instance of NetworkHandler

    def handle_client(self, client_socket, client_address):

        log = logging.getLogger(self.server_type)

        clientid = str(client_address) + ": "

        log.info(clientid + "Connected to Validation Server")

        command = client_socket.recv(13)

        log.debug(":" + binascii.b2a_hex(command[1:5]).decode("latin-1") + ":")
        log.debug(":" + binascii.b2a_hex(command).decode("latin-1") + ":")

        if command[1:5] in [b"\x00\x00\x00\x01", b"\x00\x00\x00\x03", b"\x00\x00\x00\x04"]: # TODO IMPLEMENT COMMAND 0C - validate new valve cd key
            client_socket.send(b"\x01" + real_socket.inet_aton(client_address[0]))  # CRASHES IF NOT 01 (protocol)
            ticket_full = client_socket.recv_withlen()
            ticket_full = binascii.b2a_hex(ticket_full)

            ticket_len = int(ticket_full[36:40], 16) * 2
            postticketdata = ticket_full[40 + ticket_len:]
            key = binascii.a2b_hex("10231230211281239191238542314233")
            iv = binascii.a2b_hex(postticketdata[0:32])
            encdata_len = int(postticketdata[36:40], 16) * 2
            encdata = postticketdata[40:40 + encdata_len]
            decodedmessage = binascii.b2a_hex(encryption.aes_decrypt(key, iv, binascii.a2b_hex(encdata)))
            username_len = decodedmessage[2:4] + decodedmessage[0:2]
            username = binascii.a2b_hex(decodedmessage[4:4 + int(username_len, 16) * 2])

            if (os.path.isfile("files/users/" + username.decode("latin-1") + ".py")):
                with open("files/users/" + username.decode("latin-1") + ".py", 'r') as f:
                    userblobstr = f.read()
                    userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                steamUniverse = struct.pack(">H", int(self.config["universe"]))
                steamId = steamUniverse + userblob[b'\x06\x00\x00\x00'][username][b'\x01\x00\x00\x00']
                # steamId = binascii.a2b_hex("ffffffff" + "ffffffff")
                unknown1 = binascii.a2b_hex(ticket_full[2:10])
                tms = utils.unixtime_to_steamtime(time.time())
                # key = binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059")
                ticket = unknown1 + b"\x01" + tms + steamId
                ticket_full = b"\x00\x97" + ticket
                ticket_to_sign = ticket
                ticket_signed = utilities.encryption.rsa_sign_message(encryption.network_key_sign, ticket_to_sign)
                client_socket.send(ticket_full + ticket_signed)

        client_socket.close()
        log.info(clientid + "Disconnected from Validation Server")