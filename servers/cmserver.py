import logging
import threading
import utilities.socket as emu_socket
from config import get_config as read_config
from utilities.networkhandler import TCPUDPNetworkHandler

config = read_config()


class cmserver(TCPUDPNetworkHandler):
	def __init__(self, port, config):
		super(cmserver, self).__init__(config, port)  # Create an instance of NetworkHandler

	def handle_client(self, *args):
		# Determine if the socket is TCP or UDP based on socket_type
		if args and hasattr(args[0], 'socket_type'):
			if args[0].socket_type == 'tcp':
				self.handle_client_tcp(*args)
			elif args[0].socket_type == 'udp':
				self.handle_client_udp(*args)
			else:
				raise NotImplementedError("Unknown socket type")
		else:
			raise NotImplementedError("Invalid arguments for handle_client")

	def handle_client_tcp(self, client_socket, client_address):
		log = logging.getLogger("CMTCP27014")
		clientid = str(client_address) + ": "
		log.info(f"{clientid}Connected to 27014 Server" )
		data = client_socket.recv(16234)
		log.info(data)

	def handle_client_udp(self, data, address):
		log = logging.getLogger("CMUDP27014")
		clientid = str(address) + ": "
		log.info(f"{clientid}Connected to 27014 Server" )
		log.info(data)

class cmserver2(TCPUDPNetworkHandler):
	def __init__(self, port, config):
		super(cmserver2, self).__init__(config, port)  # Create an instance of NetworkHandler

	def handle_client(self, *args):
		# Determine if the socket is TCP or UDP based on socket_type
		if args and hasattr(args[0], 'socket_type'):
			if args[0].socket_type == 'tcp':
				self.handle_client_tcp(*args)
			elif args[0].socket_type == 'udp':
				self.handle_client_udp(*args)
			else:
				raise NotImplementedError("Unknown socket type")
		else:
			raise NotImplementedError("Invalid arguments for handle_client")

	def handle_client_tcp(self, client_socket, client_address):
		log = logging.getLogger("CMTCP27017")
		clientid = str(client_address) + ": "
		log.info(f"{clientid}Connected to 27014 Server" )
		data = client_socket.recv(16234)
		log.info(data)

	def handle_client_udp(self, data, address):
		log = logging.getLogger("CMUDP27017")
		clientid = str(address) + ": "
		log.info(f"{clientid}Connected to 27014 Server" )
		log.info(data)