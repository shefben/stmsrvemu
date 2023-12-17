import ast
import binascii
import logging
import hashlib
import io
import hmac
import os
import zlib
import ipcalc
import socket as real_socket

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15

import globalvars
import utils
from utilities.database import beta1_authdb

from utilities.database.beta1_authdb import *
from utilities import blobs, encryption
from utilities.networkhandler import TCPNetworkHandler

log = logging.getLogger("B1AUTHSRV")


def load_secondblob():
	if os.path.isfile("files/secondblob.py") :
		with open("files/secondblob.py", "r") as f:
			secondblob = f.read()
		execdict = {}
		exec(secondblob, execdict)
		return blobs.blob_serialize(execdict["blob"]), secondblob
	else :
		with open("files/secondblob.bin", "rb") as f:
			bin_blob = f.read( )
		if bin_blob[0:2] == b"\x01\x43" :
			bin_blob = zlib.decompress(bin_blob[20 :])
		firstblob_unser = blobs.blob_unserialize(bin_blob)
		secondblob = "blob = " + blobs.blob_dump(firstblob_unser)
		dict_blob = ast.literal_eval(secondblob[7 :len(secondblob)])
		return dict_blob, bin_blob
class Beta1_AuthServer(TCPNetworkHandler):
	def __init__(self, port, config):
		# Create an instance of NetworkHandler
		super(Beta1_AuthServer, self).__init__(config, port)
		self.config = config

		self.dict_blob, self.blob = load_secondblob()

	def handle_client(self, client_socket, client_address):
		userdb = beta1_dbdriver(self.config)

		clientid = str(client_address) + ": "

		log.info(f"{clientid}Connected to Beta1 Authentication Server")

		if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
			islan = True
		else:
			islan = False

		msg = client_socket.recv(1)

		if msg[0] != 1:
			log.info(f"{clientid} Sent Unexpected First Byte")
			client_socket.send(b"\x00")
			return

		msg = client_socket.recv_all(4)
		version, = struct.unpack(">I", msg)
		if version == 0:
			recv_func = client_socket.recv_withlen_short
		elif version == 1:
			recv_func = client_socket.recv_withlen
		else:
			log.info(f"{clientid}Using Unrecognized version! {version}")
			client_socket.close()

		log.info(f"{clientid}Using Version: {version}")

		msg = client_socket.recv_all(4)
		client_internal_ip = msg[::-1]
		client_external_ip = real_socket.inet_aton(client_address[0])
		log.debug(f"{clientid}Internal IP: {client_internal_ip} Exernal IP: {client_external_ip}")
		client_socket.send(b"\x01" + client_external_ip[::-1])

		msg = recv_func()
		cmd = msg[0]
		log.debug(f"{clientid}Client Command: {cmd} packet: {binascii.b2a_hex(msg)}")

		if cmd == 0:
			log.info(f"{clientid} Recieved CCR (Firstblob) Request, Sending Version {version} CCR")

			if version == 0:
				client_socket.send(struct.pack("<IIIIIIII", 0, 6, 0, 0, 1, 0, 0, 0))
			elif version == 1:
				client_socket.send(struct.pack("<IIIIIIII", 0, 6, 1, 0, 1, 1, 0, 0))

			msg = client_socket.recv_all(1)
			client_socket.close()

		elif cmd == 1:  # Create User
			log.info(f"{clientid}Recieved Create User Request")
			data = bytes.fromhex("30819d300d06092a864886f70d010101050003818b0030818702818100") + encryption.network_key.n.to_bytes(128, byteorder="big") + bytes.fromhex("020111")

			client_socket.send_withlen_short(data)

			sig = pkcs1_15.new(encryption.network_key).sign(SHA1.new(data))

			client_socket.send_withlen_short(sig)

			msg = recv_func()

			bio = io.BytesIO(msg)

			size, = struct.unpack(">H", bio.read(2))
			encr_key = bio.read(size)

			sessionkey = PKCS1_OAEP.new(encryption.network_key).decrypt(encr_key)
			log.debug("session key", sessionkey.hex())

			if encryption.validate_mac(msg, sessionkey):
				log.info(f"{clientid}Message Validated OK")

			size, = struct.unpack(">I", bio.read(4))
			ctext = bio.read(size)
			ptext = encryption.beta_decrypt_message_v1(ctext[10:], sessionkey)
			log.debug(f"{clientid} Decrypted Text: ", ptext.hex())

			#pprint.pprint(blobs.blob_unserialize(ptext))

			res = userdb.create_user(ptext, version)
			if res:
				client_socket.send(b"\x01")
			else:
				client_socket.send(b"\x00")
		# login
		elif cmd == 2:
			log.info(f"{clientid}Recieved Login Request")
			bio = io.BytesIO(msg[1:])

			sz1, = struct.unpack(">H", bio.read(2))
			username1 = bio.read(sz1)

			sz2, = struct.unpack(">H", bio.read(2))
			username2 = bio.read(sz2)

			remainder = bio.read()
			if len(username1) != sz1 or len(username2) != sz2 or username1 != username2 or len(remainder) != 0:
				log.info(f"{clientid}Username1 and Username2 Do Not Match, Killing Connection!")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			log.info(f"{clientid}Attempting Login With Username: {username1}")

			salt, hash = userdb.get_salt_and_hash(username1)
			if salt is None:
				# TODO proper error to client
				log.info(f"{clientid}Incorrect Password!")
				client_socket.send(b"\x00")
				client_socket.close()
				return
			key = hash[0:16]

			client_socket.send(salt)

			if version == 0:
				msg = client_socket.recv_withlen_short()
			elif version == 1:
				msg = client_socket.recv_withlen()

			ptext = encryption.decrypt_message(msg, key)
			print(f"decrypted text: {ptext}")

			if len(ptext) != 12:
				log.info(f"{clientid}Incorrect Plaintext Size!")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			if ptext[8:12] != client_internal_ip:
				log.info(f"{clientid}Internal IP Does not match, Bad Decryption!")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			controlhash = hashlib.sha1(client_external_ip + client_internal_ip).digest()
			client_time = utils.steamtime_to_unixtime(encryption.binaryxor(ptext[0:8], controlhash[0:8]))
			skew = int(time.time() - client_time)
			if abs(skew) >= 3600:
				log.info(f"{clientid}Client Clock Skew Too Large! Disconnecting")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			userblob = userdb.get_user_blob(username1, self.dict_blob, version)
			binblob = blobs.blob_serialize(userblob)
			# just sending a plaintext blob for now

			blob_encrypted = struct.pack(">I", len(binblob)) + binblob
			currtime = int(time.time())

			innerkey = bytes.fromhex("10231230211281239191238542314233")
			times = utils.unixtime_to_steamtime(currtime) + utils.unixtime_to_steamtime(currtime + (60*60*24*28))
			if version == 1:
				steamid = bytes.fromhex("0000" + "00000000" + userblob[beta1_authdb.k(6)][username1][beta1_authdb.k(1)][0:4].hex())

				if islan == True:
					bin_ip = utils.encodeIP((self.config["server_ip"], int(self.config["validation_server_port"])))
				else:
					bin_ip = utils.encodeIP((self.config["public_ip"], int(self.config["validation_server_port"])))

				servers = bin_ip + bin_ip  # bytes.fromhex("111213149a69151617189a69")
				times = utils.unixtime_to_steamtime(currtime) + utils.unixtime_to_steamtime(currtime + (60 * 60 * 24 * 28))

				subheader = innerkey + steamid + servers + times
				subheader_encrypted = b"\x00\x00" + encryption.beta_encrypt_message(subheader, key)
			else:
				subheader = innerkey + times

				subheader_encrypted = b"\x00\x00" + encryption.beta_encrypt_message(subheader, key)

			data1_len_str = b"\x00\x80" + (b"\xff" * 0x80)

			ticket = subheader_encrypted + data1_len_str + blob_encrypted

			ticket_signed = ticket + hmac.digest(innerkey, ticket, hashlib.sha1)

			tgt_command = b"\x01" # AuthenticateAndRequestTGT command
			steamtime = utils.unixtime_to_steamtime(time.time())
			ticket_full = tgt_command + steamtime + b"\x00\xd2\x49\x6b\x00\x00\x00\x00" + struct.pack(">I", len(ticket_signed)) + ticket_signed
			log.info(f"{clientid}Sending Version {version} Ticket to client")
			client_socket.send(ticket_full)

		elif cmd in (3, 4, 5, 6, 9, 10):
			innerkey = bytes.fromhex("10231230211281239191238542314233")

			if not encryption.validate_mac(msg[1:], innerkey):
				log.info(f"{clientid}Mac Validation Failed")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			bio = io.BytesIO(msg[1:])

			ticketsize, = struct.unpack(">H", bio.read(2))
			ticket = bio.read(ticketsize)

			ptext = encryption.decrypt_message(bio.read()[:-20], innerkey)

			print("ptext", ptext.hex())
			print("ptext", repr(ptext))

			bio = io.BytesIO(ptext)

			sz1, = struct.unpack("<H", bio.read(2))
			username1 = bio.read(sz1)

			sz2, = struct.unpack("<H", bio.read(2))
			username2 = bio.read(sz2)

			if len(username1) != sz1 or len(username2) != sz2 or username1 != username2:
				log.info(f"{clientid}Username1 and Username2 Do not Match!")
				client_socket.send(b"\x00")
				client_socket.close()
				return

			print("usernames", repr(username1))

			controlhash = hashlib.sha1(client_external_ip + client_internal_ip).digest()
			client_time = utils.steamtime_to_unixtime(encryption.binaryxor(bio.read(8), controlhash[0:8]))
			skew = int(time.time() - client_time)

			print("time skew", skew)

			# delete account
			if cmd == 3:
				print(f"User requested to delete account: {username1}")
				# TODO BEN, Parse packet properly then DELETE ACCOUNT!
				client_socket.send(b"\x01")

			# logout
			elif cmd == 4:
				log.info(f"{clientid}{username1} Logged off")
				#client_socket.send(b"\x00")
				client_socket.close()
				return

			# subscribe to sub
			elif cmd == 5:
				log.info(f"{clientid}Subscription Request Recieved")
				binsubid = bio.read()
				if len(binsubid) != 4:
					log.info(f"{clientid}SubID Incorrect length (> 4 bytes) {binsubid}")
					client_socket.send(b"\x00")
					client_socket.close()
					return

				subid, = struct.unpack("<I", binsubid)

				if binsubid not in self.dict_blob[beta1_authdb.k(2)]:
					log.info(f"{clientid}Tried Adding Subscription Which Does Not Exist: {subid}")
					client_socket.send(b"\x00")
					client_socket.close()
					return

				userdb.edit_subscription(username1, subid)

				userblob = userdb.get_user_blob(username1, self.dict_blob, version)
				binblob = blobs.blob_serialize(userblob)
				log.info(f"{clientid}Successfully Subscribed to SubID: {subid}")
				client_socket.send(struct.pack(">I", len(binblob)) + binblob)

			# unsubscribe to sub
			elif cmd == 6:
				log.info(f"{clientid}Unsubscribe Request Recieved")
				binsubid = bio.read()
				if len(binsubid) != 4:
					log.info(f"{clientid}SubID Incorrect length (> 4 bytes) {binsubid}")
					client_socket.send(b"\x00")
					client_socket.close()
					return

				subid, = struct.unpack("<I", binsubid)

				if binsubid not in self.dict_blob[beta1_authdb.k(2)]:
					log.info(f"{clientid}Tried UnSubscribing Using a SubID Which Does Not Exist: {subid}")
					client_socket.send(b"\x00")
					client_socket.close()
					return

				userdb.edit_subscription(username1, subid, remove_sub=True)

				userblob = userdb.get_user_blob(username1, self.dict_blob, version)
				binblob = blobs.blob_serialize(userblob)
				log.info(f"{clientid}Successfully Unsubscribed from {subid}")
				client_socket.send(struct.pack(">I", len(binblob)) + binblob)

			# refresh info
			elif cmd == 9:
				log.info(f"{clientid}Recieved Refresh User Blob")

				userblob = userdb.get_user_blob(username1, self.dict_blob, version)
				binblob = blobs.blob_serialize(userblob)

				client_socket.send(struct.pack(">I", len(binblob)) + binblob)
			# Content Ticket
			elif cmd == 10:
				log.info(f"{clientid}Recieved Content Ticket Request")

				currtime = time.time()

				client_ticket = b"\x69" * 0x10 # key used for MAC signature
				client_ticket += utils.unixtime_to_steamtime(currtime)            # TicketCreationTime
				client_ticket += utils.unixtime_to_steamtime(currtime + 86400)    # TicketValidUntilTime

				if islan == True:
					client_ticket += utils.encodeIP((self.config["server_ip"], int(self.config["content_server_port"])))
				else:
					client_ticket += utils.encodeIP((self.config["public_ip"], int(self.config["content_server_port"])))


				server_ticket = b"\x55" * 0x80 # ticket must be between 100 and 1000 bytes

				ticket = b"\x00\x00" + encryption.beta_encrypt_message(client_ticket, innerkey)
				ticket += struct.pack(">H", len(server_ticket)) + server_ticket

				ticket_signed = ticket + hmac.digest(client_ticket[0:16], ticket, hashlib.sha1)

				# for feb2002 the ticket size is encoded as u16
				client_socket.send(b"\x00\x01" + struct.pack(">H", len(ticket_signed)) + ticket_signed)

		# Client Registry Request
		elif msg[0] == 11:
			log.info(f"{clientid}Recieved Client Registry Request")
			binblob = blobs.blob_serialize(self.blob)

			binblob = struct.pack(">I", len(binblob)) + binblob

			client_socket.send(binblob)
		# auto update??
		elif msg[0] == 13:
			log.warning(f"{clientid}Packet ID 13 (0x0d) not supported!")
			log.info(msg)
			client_socket.send(b"\x00")
		else:
			log.info(f"{clientid}Unknown Subcommand Received: {msg[0]}")
			log.debug(f"{clientid}{msg}")
			client_socket.send(b"\x00")