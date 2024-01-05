import logging

from config import get_config as read_config
from utilities.networkhandler import UDPNetworkHandler

config = read_config()


class friends(UDPNetworkHandler):
    def __init__(self, port, config):
        server_type = "friends-server"
        super(friends, self).__init__(config, int(port), server_type)

    def handle_client(self):
        # self.socket = serversocket
        log = logging.getLogger("friends")
        clientid = str(self.address) + ": "
        log.info(clientid + "Connected to Chat Server")
        # data, addr = self.socket.recvfrom(1280)
        # log.info(clientid + ("Received message: %s, from %s" % (self.data, self.addr)))
        # self.socket.sendto(self.socket, "\x00", self.addr)

        # self.socket.close()
        log.info(clientid + "Disconnected from Chat Server")