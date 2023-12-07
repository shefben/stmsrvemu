import logging
import threading

from config import get_config as read_config
from utilities.networkhandler import TCPUDPNetworkHandler

config = read_config()


class cmserver(TCPUDPNetworkHandler):
    def __init__(self, port, config):
        super(cmserver, self).__init__(config, port)  # Create an instance of NetworkHandler

    def handle_client(self, client_socket, client_address):
        self.socket = client_socket
        self.address = client_address
        log = logging.getLogger("27014")
        clientid = str(self.address) + ": "
        log.info(clientid + "Connected to 27014 Server")
        # data, addr = self.socket.recvfrom(1280)
        # log.info(clientid + ("Received message: %s, from %s" % (self.data, self.addr)))
        # self.socket.sendto(self.socket, "\x00", self.addr)

        # self.socket.close()
        log.info(clientid + "Disconnected from 27014 Server")