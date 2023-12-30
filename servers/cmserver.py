import binascii
import logging
import struct
import threading
import time
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
		dedsrv_port = client_address[1]
		#print(dedsrv_port)
		log.debug(clientid + ("Received message: %s, from %s" % (data, client_address)))
		message = binascii.b2a_hex(data)
		if message.startswith("56533031") : # VS01
			cmrecheader = message[0:8]
			cmrecsize = message[8:12]
			cmrecfamily = message[12:14]
			cmrecversion = message[14:16]
			cmrecto = message[16:24]
			cmrecfrom = message[24:32]
			cmrecsent = message[32:40]
			cmrecreceived = message[40:48]
			cmrecflag = message[48:56]
			cmrecsent2 = message[56:64]
			cmrecsize2 = message[64:72]
			cmrecdata = message[72:]

			if cmrecfamily == "01": #SendMask
				cmrepheader = cmrecheader
				cmrepsize = 4
				cmrepfamily = 2
				cmrepversion = cmrecversion
				cmrepto = cmrecfrom
				cmrepfrom = cmrecto
				cmrepsent = 1
				cmrepreceived = cmrecsent
				cmrepflag = 0
				cmrepsent2 = 0
				cmrepsize2 = 0
				cmrepdata = 0 # data empty on this packet, size is from cmrepsize (0004)
				cmmaskreply1 = cmrepheader + format(cmrepsize, '04x') + format(cmrepfamily, '02x') + cmrepversion + cmrepto + cmrepfrom + format(cmrepsent, '08x') + cmrepreceived + format(cmrepflag, '08x') + format(cmrepsent2, '08x') + format(cmrepsize2, '08x') + format(cmrepdata, '08x')
				#print(cmmaskreply1)
				cmmaskreply2 = binascii.a2b_hex(cmmaskreply1)
				#print(cmmaskreply2)
				client_socket.sendto(cmmaskreply2, client_address)
			elif cmrecfamily == "03": #SendID
				cmrepheader = cmrecheader
				cmrepsize = 0
				cmrepfamily = 4
				cmrepversion = cmrecversion

				cmrepid1 = int(round(time.time()))
				cmrepid2 = struct.pack('>I', cmrepid1)
				cmrepto = binascii.b2a_hex(cmrepid2)
				#cmrepto = cmrecfrom

				cmrepfrom = cmrecto
				cmrepsent = 2
				cmrepreceived = cmrecsent
				cmrepflag = 1
				cmrepsent2 = 2
				cmrepsize2 = 0
				cmrepdata = 0

				cmidreply1 = cmrepheader + format(cmrepsize, '04x') + format(cmrepfamily, '02x') + cmrepversion + cmrepto + cmrepfrom + format(cmrepsent, '08x') + cmrepreceived + format(cmrepflag, '08x') + format(cmrepsent2, '08x') + format(cmrepsize2, '08x') + format(cmrepdata, '08x')
				print(cmidreply1)
				cmidreply2 = binascii.a2b_hex(cmidreply1)
				print(cmidreply2)
				client_socket.sendto(cmidreply2, client_address)
			elif cmrecfamily == "07": #ProcessHeartbeat
				#if not cmrecsize == "0000":
				cmreqreq = cmrecdata[0:4]
				cmreqid = cmrecdata[4:8]
				cmreqid2 = cmrecdata[8:12]
				cmrequnknown = cmrecdata[12:16]
				cmreqdata = cmrecdata[16:]
				cmreqheader = cmrecheader

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
		log.info(f"{clientid}Connected to 27017 Server" )
		data = client_socket.recv(16234)
		log.info(data)
		if data == b'':
			client_socket.send(b"\x01")
	def handle_client_udp(self, data, address):
		log = logging.getLogger("CMUDP27017")
		clientid = str(address) + ": "
		log.info(f"{clientid}Connected to 27017 Server" )
		log.info(data)