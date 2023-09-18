import threading, logging, struct, binascii, time, atexit, socket, ipaddress, os.path, ast, csv
import os
import config
import utilities
import steamemu.logger
import socket as pysocket
import globalvars
import encryption
import steam
import globalvars

from networkhandler import UDPNetworkHandler

class trackerserver(UDPNetworkHandler) :

    def __init__(self, config, port):
        super(trackerserver, self).__init__(config, int(port))  # Create an instance of NetworkHandler

    def handle_client(self, *args):
        data, address = args
        print repr(data)
        log = logging.getLogger("TrackerSRV")
        clientid = str(address) + ": "
        log.info(clientid + "Connected to Tracker Server")

        ticket_full = data
        ticket_full = binascii.b2a_hex(ticket_full)

        key = binascii.a2b_hex("10231230211281239191238542314233")
        iv = binascii.a2b_hex(postticketdata[0:32])
        encdata_len = int(postticketdata[36:40], 16) * 2
        encdata = postticketdata[40:40 + encdata_len]
        decodedmessage = binascii.b2a_hex(
            encryption.aes_decrypt(key, iv, binascii.a2b_hex(data)))
        print(repr(decodedmessage))
        log.debug(clientid + ("Received encryptedmessage: %s, from %s" % (data, address)))
        ipstr = str(address)
        ipstr1 = ipstr.split('\'')
        ipactual = ipstr1[1]
        log.info(clientid + data)

        #if data.startswith("e"):  # 65
        #    self.socket.sendto("\xFF\xFF\xFF\xFF\x68\x01"+"thank you\n\0", address)
        #else:
        #    log.info("Unknown Harvester command: %s" % data)