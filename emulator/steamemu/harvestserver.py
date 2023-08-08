import threading, logging, struct, binascii, time, socket, ipaddress, os.path, ast, csv, atexit
import os
import utilities
import config
import steamemu.logger
import globalvars
import socket as pysocket

from networkhandler import UDPNetworkHandler

class harvestserver(UDPNetworkHandler):
    def __init__(self, config, port):
        server_type = "harvestserver"
        super(harvestserver, self).__init__(config, int(port), server_type)  # Create an instance of NetworkHandler

        
        thread2 = threading.Thread(target=self.heartbeat_thread)
        thread2.daemon = True
        thread2.start()
        
    def handle_client(self, *args):
        data, address = args
        log = logging.getLogger("HarvestSRV")
        # Process the received packet
        clientid = str(address) + ": "
        log.info(clientid + "Connected to Harvest MiniDump Collection Server")
        log.debug(clientid + ("Received message: %s, from %s" % (data, address)))
        ipstr = str(address)
        ipstr1 = ipstr.split('\'')
        ipactual = ipstr1[1]
        log.info(clientid + data)
        #if data.startswith("e"):  # 65
        #    self.socket.sendto("\xFF\xFF\xFF\xFF\x68\x01"+"thank you\n\0", address)
        #else:
        #    log.info("Unknown Harvester command: %s" % data)



