import threading, logging, struct, binascii, time, atexit, ipaddress, os.path, ast, csv
import socket as pysocket
import os
import config
import utilities
import steam
import globalvars
import emu_socket
import steamemu.logger
import encryption
from networkhandler import TCPNetworkHandler

log = logging.getLogger("validationsrv")

class validationserver(TCPNetworkHandler):
    log = logging.getLogger("ValidationSRV")
       
    def __init__(self, port, config):
        server_type = "validationserver"
        super(validationserver, self).__init__(config, port, server_type)  # Create an instance of NetworkHandler

    def handle_client(self, clientsocket, address):
        #threading.Thread.__init__(self)
        clientid = str(address) + ": "

        log.info(clientid + "Connected to Validation Server")

        command = clientsocket.recv(13)

        log.debug(":" + binascii.b2a_hex(command[1:5]) + ":")
        log.debug(":" + binascii.b2a_hex(command) + ":")

        if command[1:5] == "\x00\x00\x00\x04" :

            clientsocket.send("\x01" + pysocket.inet_aton(address[0])) #CRASHES IF NOT 01 (protocol)
            ticket_full = clientsocket.recv_withlen()
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
            userblob = {}
            if (os.path.isfile("files/users/" + username + ".py")) :
                with open("files/users/" + username + ".py", 'r') as f:
                    userblobstr = f.read()
                    userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                steamId = userblob['\x06\x00\x00\x00'][username]['\x01\x00\x00\x00']
                unknown1 = binascii.a2b_hex(ticket_full[2:10])
                tms = utilities.unixtime_to_steamtime(time.time())
                #key = binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059")
                ticket = "\x00\x97" + unknown1 + "\x01" + tms + "\x00\x00" + steamId
                ticket_to_sign = unknown1 + "\x01" + tms + "\x00\x00" + steamId
                ticket_signed = encryption.rsa_sign_message(encryption.network_key_sign, ticket_to_sign)
                clientsocket.send("\x00\x97" + unknown1 + "\x01" + tms + "\x00\x00" + steamId + ticket_signed)

        clientsocket.close()
        log.info(clientid + "Disconnected from Validation Server")
