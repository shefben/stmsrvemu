

import binascii
import hashlib
import hmac
import io
import os
import os.path
import pickle
import threading
import time
import zlib
from time import sleep

import ipcalc
from Crypto.Hash import SHA

import globalvars
import utilities.blobs
import utilities.encryption
import utilities.storages
import utils
from gcf_to_storage import gcf2storage
from listmanagers.contentlistmanager import manager
from listmanagers.contentserverlist_utilities import send_heartbeat
from utilities import cdr_manipulator, encryption
from utilities.checksums import Checksum2, Checksum3
from utilities.manifests import *
from utilities.networkhandler import TCPNetworkHandler

app_list = []
csConnectionCount = 0


class contentserver(TCPNetworkHandler):

	def __init__(self, port, config):
		global app_list
		super(contentserver, self).__init__(config, port)  # Create an instance of NetworkHandler
		if globalvars.public_ip == "0.0.0.0" :
			server_ip = globalvars.server_ip
		else:
			server_ip = globalvars.public_ip
		self.contentserver_info = {
			'wan_ip' : server_ip,
			'lan_ip' : globalvars.server_ip,
			'port': int(port),
			'region': globalvars.cs_region,
			'timestamp': 1623276000
		}

		if not globalvars.aio_server:
			self.applist = self.parse_manifest_files(self.contentserver_info)
			self.thread2 = threading.Thread(target=self.heartbeat_thread)
			self.thread2.daemon = True
			self.thread2.start()
		else:
			self.parse_manifest_files(self.contentserver_info)
			manager.add_contentserver_info(server_ip, globalvars.server_ip, int(port), globalvars.cs_region, app_list, 1)

	def heartbeat_thread(self):
		while True:
			send_heartbeat(self.contentserver_info, self.applist)
			time.sleep(1800)  # 30 minutes

	def handle_client(self, client_socket, client_address):
		global csConnectionCount

		if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
			islan = True
		else:
			islan = False

		log = logging.getLogger("ContentServer")
		clientid = str(client_address) + ": "
		log.info(f"{clientid}Connected to Content Server")

		msg = client_socket.recv(4)
		csConnectionCount += 1

		if len(msg) == 0:
			log.info(f"{clientid}Got simple handshake. Closing connection.")

		elif msg in [b"\x00\x00\x00\x00", b"\x00\x00\x00\x01"]: # beta 1 version 0 & Beta1 Version 1
			log.info(f"{clientid}Storage mode entered")

			storagesopen = 0
			storages = {}

			client_socket.send(b"\x01")  # this should just be the handshake

			if msg == b"\x00\x00\x00\x01":
				command = client_socket.recv_withlen()
			else:
				command = client_socket.recv_withlen_short()

			if command[0:1] == b"\x00":
				(connid, messageid, app, version) = struct.unpack(">IIII", command[1:17])

				(app, version) = struct.unpack(">II", command[1:9])
				log.debug(f"{clientid}appid: {app}, verid: {version}" )

				connid |= 0x80000000
				key = b"\x69" * 0x10
				if encryption.validate_mac(command[9:], key):
					log.debug(clientid + repr(encryption.validate_mac(command[9:], key)))

				# TODO BEN, DO PROPER TICKET VALIDATION
				# bio = io.BytesIO(command[9:])

				# ticketsize, = struct.unpack(">H", bio.read(2))
				# ticket = bio.read(ticketsize)

				# ptext = encryption.decrypt_message(bio.read()[:-20], key)
				log.info(f"{clientid}Opening application {app} {version}" )
				try:
					s = utilities.storages.Storage(app, self.config["storagedir"], version)
				except Exception:
					log.error("Application not installed! %d %d" % (app, version))

					# reply = struct.pack(">LLc", connid, messageid, b"\x01")
					reply = struct.pack(">B", 0)
					client_socket.send(reply)
					return

				storageid = storagesopen
				storagesopen += 1

				storages[storageid] = s
				storages[storageid].app = app
				storages[storageid].version = version

				if os.path.isfile(self.config["betamanifestdir/beta1"] + str(app) + "_" + str(version) + ".manifest"):
					f = open(self.config["betamanifestdir/beta1"] + str(app) + "_" + str(version) + ".manifest", "rb")
					log.info(f"{clientid}{app}_{version} is a beta depot" )
				else:
					log.error(f"Manifest not found for {app} {version} " )
					# reply = struct.pack(">LLc", connid, messageid, b"\x01")
					client_socket.send(b"\x00")
					return
				manifest = f.read()
				f.close()

				manifest_appid = struct.unpack('<L', manifest[4:8])[0]
				manifest_verid = struct.unpack('<L', manifest[8:12])[0]
				log.debug(f"{clientid}Manifest ID: {manifest_appid} Version: {manifest_verid}" )
				if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)):
					log.error(f"Manifest doesn't match requested file: ({app}, {version}) ({manifest_appid}, {manifest_verid})" )

					# reply = struct.pack(">LLc", connid, messageid, b"\x01")
					client_socket.send(b"\x00")
					return

				globalvars.converting = "0"

				fingerprint = manifest[0x30:0x34]
				oldchecksum = manifest[0x34:0x38]
				manifest = manifest[:0x30] + b"\x00" * 8 + manifest[0x38:]
				checksum = struct.pack("<I", zlib.adler32(manifest, 0))
				manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]

				log.debug(f"Checksum fixed from  {binascii.b2a_hex(oldchecksum)}  to {binascii.b2a_hex(checksum)}")

				storages[storageid].manifest = manifest

				checksum = struct.unpack("<L", manifest[0x30:0x34])[0]  # FIXED, possible bug source

				# reply = struct.pack(">LLcLL", connid, messageid, b"\x00", storageid, checksum)
				reply = b"\x66" + fingerprint[::-1] + b"\x01"

				client_socket.send(reply, False)

				index_file = self.config["betastoragedir/beta1"] + str(app) + "_" + str(version) + ".index"
				dat_file = self.config["betastoragedir/beta1"] + str(app) + "_" + str(version) + ".dat"
				# Load the index
				with open(index_file, 'rb') as f:
					index_data = pickle.load(f)
				try:
					dat_file_handle.close()
				except:
					pass
				dat_file_handle = open(dat_file, 'rb')
				while True:
					command = client_socket.recv(1)
					if len(command) == 0:
						log.info(f"{clientid}Disconnected from Content Server" )
						client_socket.close()
						return

					if command[0:1] == b"\x01":  # HANDSHAKE
						client_socket.send(b"")
						break

					elif command[0:1] in [b"\x02",b"\x04"] : #SEND MANIFEST AGAIN
						log.info(f"{clientid}Sending manifest")
						client_socket.send(struct.pack(">I", len(manifest)) + manifest, False)

					elif command[0:1] == b"\x03":  # CLOSE STORAGE
						(storageid, messageid) = struct.unpack(">xLL", command)
						del storages[storageid]
						reply = struct.pack(">LLc", storageid, messageid, b"\x00")
						log.info(f"{clientid}Closing down storage {storageid}")
						client_socket.send(reply)
					elif command[0:1] == b"\x05":  # SEND DATA
						msg = client_socket.recv(12)
						fileid, offset, length = struct.unpack(">III", msg)
						index_file = self.config["betastoragedir/beta1"] + str(app) + "_" + str(version) + ".index"
						dat_file = self.config["betastoragedir/beta1"] + str(app) + "_" + str(version) + ".dat"
						if islan:
							filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "internal")
						else:
							filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "external")
						# 0000001a 00000000 00010000
						# 00000001 00000000 00001e72
						client_socket.send(b"\x01" + struct.pack(">II", len(filedata), 0), False)
						for i in range(0, len(filedata), 0x2000):
							chunk = filedata[i:i + 0x2000]
							client_socket.send(struct.pack(">I", len(chunk)) + chunk, False)
						# client_socket.send(struct.pack(">I", len(filedata)) + filedata, False)

		elif msg == b"\x00\x00\x00\x02":  # \x02 for 2003 beta v2 content
			log.info(f"{clientid}Storage mode entered")

			storagesopen = 0
			storages = {}

			client_socket.send(b"\x01")  # this should just be the handshake

			while True:

				command = client_socket.recv_withlen()

				if command[0:1] == b"\x00" : #SEND MANIFEST AND PROCESS RESPONSE

					(connid, messageid, app, version) = struct.unpack(">IIII", command[1:17])
					# print(connid, messageid, app, version)
					# print(app)
					# print(version)

					(app, version) = struct.unpack(">II", command[1:9])
					log.debug(clientid + "appid: " + str(int(app)) + ", verid: " + str(int(version)))

					# bio = io.BytesIO(msg[9:])

					# ticketsize, = struct.unpack(">H", bio.read(2))
					# ticket = bio.read(ticketsize)

					connid |= 0x80000000
					key = b"\x69" * 0x10
					if encryption.validate_mac(command[9:], key):
						log.debug(clientid + repr(encryption.validate_mac(command[9:], key)))
					# TODO BEN, DO PROPER TICKET VALIDATION
					# print(binascii.b2a_hex(signeddata))

					# if hmac.new(key, signeddata[:-20], hashlib.sha1).digest() == signeddata[-20:]:
					#    log.debug(clientid + "HMAC verified OK")
					# else:
					#    log.error(clientid + "BAD HMAC")
					#    raise Exception("BAD HMAC")

					# bio = io.BytesIO(msg[9:]) #NOT WORKING, UNKNOWN KEY
					# print(bio)
					# ticketsize, = struct.unpack(">H", bio.read(2))
					# print(ticketsize)
					# ticket = bio.read(ticketsize)
					# print(binascii.b2a_hex(ticket))
					# postticketdata = io.BytesIO(bio.read()[:-20])
					# IV = postticketdata.read(16)
					# print(len(IV))
					# print(binascii.b2a_hex(IV))
					# enclen = postticketdata.read(2)
					# print(binascii.b2a_hex(enclen))
					# print(struct.unpack(">H", enclen)[0])
					# enctext = postticketdata.read(struct.unpack(">H", enclen)[0])
					# print(binascii.b2a_hex(enctext))
					# ptext = utils.aes_decrypt(key, IV, enctext)
					# print(binascii.b2a_hex(ptext))

					log.info(f"{clientid}Opening application %d %d" % (app, version))
					# connid = pow(2,31) + connid

					try:
						s = utilities.storages.Storage(app, self.config["storagedir"], version)
					except Exception:
						log.error("Application not installed! %d %d" % (app, version))

						# reply = struct.pack(">LLc", connid, messageid, b"\x01")
						reply = struct.pack(">B", 0)
						client_socket.send(reply)

						break

					storageid = storagesopen
					storagesopen += 1

					storages[storageid] = s
					storages[storageid].app = app
					storages[storageid].version = version

					if os.path.isfile(self.config["betamanifestdir"] + str(app) + "_" + str(version) + ".manifest"):
						f = open(self.config["betamanifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
						log.info(f"{clientid}{app}_{version} is a beta depot" )
					else:
						log.error(f"Manifest not found for {app} {version} " )
						# reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(b"\x00")
						break
					manifest = f.read()
					f.close()

					manifest_appid = struct.unpack('<L', manifest[4:8])[0]
					manifest_verid = struct.unpack('<L', manifest[8:12])[0]
					log.debug(f"{clientid}Manifest ID: {manifest_appid} Version: {manifest_verid}" )
					if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)):
						log.error(f"Manifest doesn't match requested file: ({app}, {version}) ({manifest_appid}, {manifest_verid})" )

						# reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(b"\x00")

						break

					globalvars.converting = "0"

					fingerprint = manifest[0x30:0x34]
					oldchecksum = manifest[0x34:0x38]
					manifest = manifest[:0x30] + b"\x00" * 8 + manifest[0x38:]
					checksum = struct.pack("<I", zlib.adler32(manifest, 0))
					manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]

					log.debug(f"Checksum fixed from  {binascii.b2a_hex(oldchecksum)}  to {binascii.b2a_hex(checksum)}")

					storages[storageid].manifest = manifest

					checksum = struct.unpack("<L", manifest[0x30:0x34])[0]  # FIXED, possible bug source

					# reply = struct.pack(">LLcLL", connid, messageid, b"\x00", storageid, checksum)
					reply = b"\xff" + fingerprint[::-1]

					client_socket.send(reply, False)

					index_file = self.config["betastoragedir"] + str(app) + "_" + str(version) + ".index"
					dat_file = self.config["betastoragedir"] + str(app) + "_" + str(version) + ".dat"
					# Load the index
					with open(index_file, 'rb') as f:
						index_data = pickle.load(f)
					try:
						dat_file_handle.close()
					except:
						pass
					dat_file_handle = open(dat_file, 'rb')

					while True:
						command = client_socket.recv(1)

						if len(command) == 0:
							log.info(f"{clientid}Disconnected from Content Server" )
							client_socket.close()
							return

						if command[0:1] == b"\x02" : #SEND MANIFEST AGAIN

							log.info(f"{clientid}Sending manifest")

							# (storageid, messageid) = struct.unpack(">xLL", command)

							# manifest = storages[storageid].manifest

							# reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(manifest))
							# reply = struct.pack(">BL", 0, len(manifest))
							# print(binascii.b2a_hex(reply))

							# client_socket.send(reply)

							# reply = struct.pack(">LLL", storageid, messageid, len(manifest))
							reply = struct.pack(">L", len(manifest))
							#print(binascii.b2a_hex(reply))

							#print(binascii.b2a_hex(manifest))

							client_socket.send(b"\x01" + reply + manifest, False)

						elif command[0:1] == b"\x01":  # HANDSHAKE

							client_socket.send(b"")
							break

						elif command[0:1] == b"\x03":  # CLOSE STORAGE

							(storageid, messageid) = struct.unpack(">xLL", command)

							del storages[storageid]

							reply = struct.pack(">LLc", storageid, messageid, b"\x00")

							log.info(f"{clientid}Closing down storage {storageid}")

							client_socket.send(reply)

						elif command[0:1] == b"\x04":  # SEND MANIFEST

							log.info(f"{clientid}Sending manifest")

							# (storageid, messageid) = struct.unpack(">xLL", command)

							# manifest = storages[storageid].manifest

							# reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(manifest))
							# reply = struct.pack(">BL", 0, len(manifest))
							# print(binascii.b2a_hex(reply))

							# client_socket.send(reply)

							# reply = struct.pack(">LLL", storageid, messageid, len(manifest))
							reply = struct.pack(">L", len(manifest))
							#print(binascii.b2a_hex(reply))

							#print(binascii.b2a_hex(manifest))

							client_socket.send(b"\x01" + reply + manifest, False)

						elif command[0:1] == b"\x25":  # SEND UPDATE INFO - DISABLED WAS \x05
							log.info(f"{clientid}Sending app update information")
							(storageid, messageid, oldversion) = struct.unpack(">xLLL", command)
							appid = storages[storageid].app
							version = storages[storageid].version
							log.info(f"Old GCF version: {appid}_{oldversion}" )
							log.info(f"New GCF version: {appid}_{version}" )
							manifestNew = Manifest2(appid, version)
							manifestOld = Manifest2(appid, oldversion)

							if os.path.isfile(
									self.config["v2manifestdir"] + str(appid) + "_" + str(version) + ".manifest"):
								checksumNew = Checksum3(appid)
							else:
								checksumNew = Checksum2(appid, version)

							if os.path.isfile(
									self.config["v2manifestdir"] + str(appid) + "_" + str(oldversion) + ".manifest"):
								checksumOld = Checksum3(appid)
							else:
								checksumOld = Checksum2(appid, version)

							filesOld = {}
							filesNew = {}
							for n in manifestOld.nodes.values():
								if n.fileId != 0xffffffff:
									n.checksum = checksumOld.getchecksums_raw(n.fileId)
									filesOld[n.fullFilename] = n

							for n in manifestNew.nodes.values():
								if n.fileId != 0xffffffff:
									n.checksum = checksumNew.getchecksums_raw(n.fileId)
									filesNew[n.fullFilename] = n

							del manifestNew
							del manifestOld

							changedFiles = []

							for filename in filesOld:
								if filename in filesNew and filesOld[filename].checksum != filesNew[filename].checksum:
									changedFiles.append(filesOld[filename].fileId)
									log.debug(f"Changed file: {filename} : {filesOld[filename].fileId}" )
								if not filename in filesNew:
									changedFiles.append(filesOld[filename].fileId)
									# if not 0xffffffff in changedFiles:
									# changedFiles.append(0xffffffff)
									log.debug(f"Deleted file: {filename} : {filesOld[filename].fileId}" )

							for x in range(len(changedFiles)):
								log.debug(changedFiles[x], )

							count = len(changedFiles)
							log.info(f"Number of changed files: {count}" )

							if count == 0:
								reply = struct.pack(">LLcL", storageid, messageid, b"\x01", 0)
								client_socket.send(reply)
							else:
								reply = struct.pack(">LLcL", storageid, messageid, b"\x02", count)
								client_socket.send(reply)

								changedFilesTmp = []
								for fileid in changedFiles:
									changedFilesTmp.append(struct.pack("<L", fileid))
								updatefiles = b"".join(changedFilesTmp)

								reply = struct.pack(">LL", storageid, messageid)
								client_socket.send(reply)
								client_socket.send_withlen(updatefiles)

						elif command[0:1] == b"\x05":  # SEND DATA
							msg = client_socket.recv(12)
							fileid, offset, length = struct.unpack(">III", msg)
							index_file = self.config["betastoragedir"] + str(app) + "_" + str(version) + ".index"
							dat_file = self.config["betastoragedir"] + str(app) + "_" + str(version) + ".dat"
							if islan == True:
								filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "internal")
							else:
								filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "external")
							# 0000001a 00000000 00010000
							# 00000001 00000000 00001e72
							client_socket.send(b"\x01" + struct.pack(">II", len(filedata), 0), False)
							for i in range(0, len(filedata), 0x2000):
								chunk = filedata[i:i + 0x2000]
								client_socket.send(struct.pack(">I", len(chunk)) + chunk, False)
							# client_socket.send(struct.pack(">I", len(filedata)) + filedata, False)

						elif command[0:1] == b"\x06":  # BANNER

							if len(command) == 10:
								client_socket.send(b"\x01")
								break
							else:
								log.info(f"Banner message: {binascii.b2a_hex(command)}")

								if self.config["http_port"] == "steam" or self.config["http_port"] == "0" or globalvars.steamui_ver < 87 :
									if islan:
										url = ("http://" + self.config["http_ip"] + "/platform/banner/random.php").encode("latin-1")
										#print("INTERNAL BANNER")
									else:
										url = ("http://" + self.config["public_ip"] + "/platform/banner/random.php").encode("latin-1")
										#print("EXTERNAL BANNER")
									#url = b"about:blank"
								else :
									url = b"about:blank"

								reply = struct.pack(">H", len(url)) + url

								client_socket.send(reply)

						elif command[0:1] == b"\x07":  # SEND DATA

							(storageid, messageid, fileid, filepart, numparts, priority) = struct.unpack(">xLLLLLB",
																									   command)

							(chunks, filemode) = storages[storageid].readchunks(fileid, filepart, numparts)

							reply = struct.pack(">LLcLL", storageid, messageid, b"\x00", len(chunks), filemode)

							client_socket.send(reply, False)

							for chunk in chunks:
								reply = struct.pack(">LLL", storageid, messageid, len(chunk))

								client_socket.send(reply, False)

								reply = struct.pack(">LLL", storageid, messageid, len(chunk))

								client_socket.send(reply, False)

								client_socket.send(chunk, False)

						elif command[0:1] == b"\x08":  # INVALID

							log.warning("08 - Invalid Command!")
							client_socket.send(b"\x01")
						else:

							log.warning(f"{binascii.b2a_hex(command[0:1])} - Invalid Command!")
							client_socket.send(b"\x01")

							break

					try:
						dat_file_handle.close()
					except:
						pass
				else:

					log.warning(f"{binascii.b2a_hex(command[0:1])} - Invalid Command!")
					client_socket.send(b"\x01")

					break

		elif msg == b"\x00\x00\x00\x05" or msg == b"\x00\x00\x00\x06":  # \x06 for 2003 release

			log.info(f"{clientid}Storage mode entered")

			storagesopen = 0
			storages = {}

			client_socket.send(b"\x01")  # this should just be the handshake

			while True:

				command = client_socket.recv_withlen()

				if command[0:1] == b"\x00":  # BANNER

					if len(command) == 10:
						client_socket.send(b"\x01")
						break
					else:
						log.info(f"Banner message: {binascii.b2a_hex(command)}")

						if self.config["http_port"] == "steam" or self.config[
							"http_port"] == "0" or globalvars.steamui_ver < 87:
							if self.config["public_ip"] != "0.0.0.0":
								url = "http://" + self.config["public_ip"] + "/platform/banner/random.php"
							else:
								url = "http://" + self.config["http_ip"] + "/platform/banner/random.php"
						else:
							if self.config["public_ip"] != "0.0.0.0":
								url = "http://" + self.config["public_ip"] + ":" + self.config[
									"http_port"] + "/platform/banner/random.php"
							else:
								url = "http://" + self.config["http_ip"] + ":" + self.config[
									"http_port"] + "/platform/banner/random.php"

						reply = struct.pack(">BH", 1, len(url)) + url.encode()

						client_socket.send(reply)

				elif command[0:1] == b"\x02":  # SEND MANIFEST

					if globalvars.steamui_ver < 24:
						(connid, messageid, app, version) = struct.unpack(">IIII", command[1:17])
						# print(connid, messageid, app, version)
						# print(app)
						# print(version)
						connid |= 0x80000000
						key = b"\x69" * 0x10
						signeddata = command[17:]
						# print(binascii.b2a_hex(signeddata))

						if hmac.new(key, signeddata[:-20], hashlib.sha1).digest() == signeddata[-20:]:
							log.debug(clientid + "HMAC verified OK")
						else:
							log.error(clientid + "BAD HMAC")
							raise Exception("BAD HMAC")

						bio = io.BytesIO(signeddata)
						# print(bio)
						ticketsize, = struct.unpack(">H", bio.read(2))
						# print(ticketsize)
						ticket = bio.read(ticketsize)
						# print(binascii.b2a_hex(ticket))
						postticketdata = bio.read()[:-20]
						IV = postticketdata[0:16]
						# print(len(IV))
						# print(len(postticketdata))
						ptext = utilities.encryption.aes_decrypt(key, IV, postticketdata[4:])
						log.info(f"{clientid}Opening application {app}, {version}")
						# connid = pow(2,31) + connid

						try:
							s = utilities.storages.Storage(app, self.config["storagedir"], version)
						except Exception:
							log.error(f"Application not installed! {app}, {version}")

							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)

							break
						storageid = storagesopen
						storagesopen = storagesopen + 1

						storages[storageid] = s
						storages[storageid].app = app
						storages[storageid].version = version

						if str(app) == "3" or str(app) == "7":
							if not os.path.isfile(
									"files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
										version) + ".manifest"):
								if os.path.isfile("files/convert/" + str(app) + "_" + str(version) + ".gcf"):
									log.info("Fixing files in app " + str(app) + " version " + str(version))
									g = open("files/convert/" + str(app) + "_" + str(version) + ".gcf", "rb")
									file = g.read()
									g.close()
									for (search, replace, info) in globalvars.replace_string:
										fulllength = len(search)
										newlength = len(replace)
										missinglength = fulllength - newlength
										if missinglength < 0:
											print(b"WARNING: Replacement text " + replace + b" is too long! Not replaced!")
										elif missinglength == 0:
											file = file.replace(search, replace)
											print (f"Replaced {info}")
										else:
											file = file.replace(search, replace + (b'\x00' * missinglength))
											print (f"Replaced {info}")

									h = open("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf", "wb")
									h.write(file)
									h.close()
									gcf2storage("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")
									sleep(1)
									os.remove("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")

						if os.path.isfile("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(version) + ".manifest"):
							f = open("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(version) + ".manifest", "rb")
							log.info(clientid + str(app) + "_" + str(version) + " is a cached depot")
						elif os.path.isfile(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
							f = open(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
							log.info(clientid + str(app) + "_" + str(version) + " is a v0.2 depot")
						elif os.path.isfile(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
							f = open(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
							log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 depot")
						elif os.path.isdir(self.config["v3manifestdir2"]):
							if os.path.isfile(
									self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest"):
								f = open(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest",
										 "rb")
								log.info(f"{clientid}{app}_{version} is a v0.3 extra depot" )
							else:
								log.error(f"Manifest not found for {app} {version} " )
								reply = struct.pack(">LLc", connid, messageid, b"\x01")
								client_socket.send(reply)
								break
						else:
							log.error(f"Manifest not found for {app} {version} " )
							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)
							break
						manifest = f.read()
						f.close()

						manifest_appid = struct.unpack('<L', manifest[4:8])[0]
						manifest_verid = struct.unpack('<L', manifest[8:12])[0]
						log.debug(f"{clientid}Manifest ID: {manifest_appid} Version: {manifest_verid}")
						if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)):
							log.error(f"Manifest doesn't match requested file: ({app}, {version}) ({manifest_appid}, {manifest_verid})" )

							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)

							break

						globalvars.converting = "0"

						fingerprint = manifest[0x30:0x34]
						oldchecksum = manifest[0x34:0x38]
						manifest = manifest[:0x30] + b"\x00" * 8 + manifest[0x38:]
						checksum = struct.pack("<I", zlib.adler32(manifest, 0))
						manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]

						log.debug(f"Checksum fixed from {binascii.b2a_hex(oldchecksum).decode('latin-1')}  to {binascii.b2a_hex(checksum).decode('latin-1')}")

						storages[storageid].manifest = manifest

						checksum = struct.unpack("<L", manifest[0x30:0x34])[0]  # FIXED, possible bug source

						reply = struct.pack(">LLcLL", connid, messageid, b"\x00", storageid, checksum)

						client_socket.send(reply, False)
					else:
						a = 1  # DUMMY, TAKE OUT

				elif command[0:1] == b"\x09" or command[0:1] == b"\x0a" or command[
					0] == b"\x02":  # REQUEST MANIFEST #09 is used by early clients without a ticket# 02 used by 2003 steam

					if command[0:1] == b"\x0a":
						log.info(f"{clientid}Login packet used")
					# else :
					# log.error(clientid + "Not logged in")

					# reply = struct.pack(">LLc", connid, messageid, b"\x01")
					# client_socket.send(reply)

					# break

					(connid, messageid, app, version) = struct.unpack(">xLLLL", command[0:17])

					log.info(f"{clientid}Opening application {app}, {version}")
					connid = pow(2, 31) + connid

					try:
						s = utilities.storages.Storage(app, self.config["storagedir"], version)
					except Exception:
						log.error("Application not installed! {app}, {version}")

						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)

						break

					storageid = storagesopen
					storagesopen = storagesopen + 1

					storages[storageid] = s
					storages[storageid].app = app
					storages[storageid].version = version

					if str(app) == "3" or str(app) == "7":
						if not os.path.isfile(
								"files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
									version) + ".manifest"):
							if os.path.isfile("files/convert/" + str(app) + "_" + str(version) + ".gcf"):
								log.info("Fixing files in app " + str(app) + " version " + str(version))
								g = open("files/convert/" + str(app) + "_" + str(version) + ".gcf", "rb")
								file = g.read()
								g.close()
								for (search, replace, info) in globalvars.replace_string(islan):
									fulllength = len(search)
									newlength = len(replace)
									missinglength = fulllength - newlength
									if missinglength < 0:
										print(b"WARNING: Replacement text " + replace + b" is too long! Not replaced!")
									elif missinglength == 0:
										file = file.replace(search, replace)
										print(b"Replaced", info)
									else:
										file = file.replace(search, replace + (b'\x00' * missinglength))
										print(b"Replaced", info)

								h = open("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf", "wb")
								h.write(file)
								h.close()
								gcf2storage("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")
								sleep(1)
								os.remove("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")

					if os.path.isfile("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
							version) + ".manifest"):
						f = open("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
							version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a cached depot")
					elif os.path.isfile(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
						f = open(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a v0.2 depot")
					elif os.path.isfile(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
						f = open(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 depot")
					elif os.path.isdir(self.config["v3manifestdir2"]):
						if os.path.isfile(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest"):
							f = open(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest", "rb")
							log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 extra depot")
						else:
							log.error(f"Manifest not found for {app} {version} " )
							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)
							break
					else:
						log.error(f"Manifest not found for {app} {version} " )
						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)
						break
					manifest = f.read()
					f.close()

					manifest_appid = struct.unpack('<L', manifest[4:8])[0]
					manifest_verid = struct.unpack('<L', manifest[8:12])[0]
					log.debug(clientid + ("Manifest ID: %s Version: %s" % (manifest_appid, manifest_verid)))
					if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)):
						log.error(f"Manifest doesn't match requested file: ({app}, {version}) ({manifest_appid}, {manifest_verid})" )

						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)

						break

					globalvars.converting = "0"

					fingerprint = manifest[0x30:0x34]
					oldchecksum = manifest[0x34:0x38]
					manifest = manifest[:0x30] + b"\x00" * 8 + manifest[0x38:]
					checksum = struct.pack("<I", zlib.adler32(manifest, 0))
					manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]

					log.debug(b"Checksum fixed from " + binascii.b2a_hex(oldchecksum) + b" to " + binascii.b2a_hex(checksum))

					storages[storageid].manifest = manifest

					checksum = struct.unpack("<L", manifest[0x30:0x34])[0]  # FIXED, possible bug source

					reply = struct.pack(">LLcLL", connid, messageid, b"\x00", storageid, checksum)

					client_socket.send(reply, False)

				elif command[0:1] == b"\x01":  # HANDSHAKE

					client_socket.send(b"")
					break

				elif command[0:1] == b"\x03":  # CLOSE STORAGE

					(storageid, messageid) = struct.unpack(">xLL", command)

					del storages[storageid]

					reply = struct.pack(">LLc", storageid, messageid, b"\x00")

					log.info(f"{clientid}Closing down storage %d" % storageid)

					client_socket.send(reply)

				elif command[0:1] == b"\x04":  # SEND MANIFEST

					log.info(f"{clientid}Sending manifest")

					(storageid, messageid) = struct.unpack(">xLL", command)

					manifest = storages[storageid].manifest

					reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(manifest))

					client_socket.send(reply)

					reply = struct.pack(">LLL", storageid, messageid, len(manifest))

					client_socket.send(reply + manifest, False)

				elif command[0:1] == b"\x05":  # SEND UPDATE INFO
					log.info(f"{clientid}Sending app update information")
					(storageid, messageid, oldversion) = struct.unpack(">xLLL", command)
					appid = storages[storageid].app
					version = storages[storageid].version
					log.info("Old GCF version: " + str(appid) + "_" + str(oldversion))
					log.info("New GCF version: " + str(appid) + "_" + str(version))
					manifestNew = Manifest2(appid, version)
					manifestOld = Manifest2(appid, oldversion)

					if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(version) + ".manifest"):
						checksumNew = Checksum3(appid)
					else:
						checksumNew = Checksum2(appid, version)

					if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(oldversion) + ".manifest"):
						checksumOld = Checksum3(appid)
					else:
						checksumOld = Checksum2(appid, version)

					filesOld = {}
					filesNew = {}
					for n in manifestOld.nodes.values():
						if n.fileId != 0xffffffff:
							n.checksum = checksumOld.getchecksums_raw(n.fileId)
							filesOld[n.fullFilename] = n

					for n in manifestNew.nodes.values():
						if n.fileId != 0xffffffff:
							n.checksum = checksumNew.getchecksums_raw(n.fileId)
							filesNew[n.fullFilename] = n

					del manifestNew
					del manifestOld

					changedFiles = []

					for filename in filesOld:
						if filename in filesNew and filesOld[filename].checksum != filesNew[filename].checksum:
							changedFiles.append(filesOld[filename].fileId)
							log.debug("Changed file: " + str(filename) + " : " + str(filesOld[filename].fileId))
						if not filename in filesNew:
							changedFiles.append(filesOld[filename].fileId)
							# if not 0xffffffff in changedFiles:
							# changedFiles.append(0xffffffff)
							log.debug("Deleted file: " + str(filename) + " : " + str(filesOld[filename].fileId))

					for x in range(len(changedFiles)):
						log.debug(changedFiles[x], )

					count = len(changedFiles)
					log.info("Number of changed files: " + str(count))

					if count == 0:
						reply = struct.pack(">LLcL", storageid, messageid, b"\x01", 0)
						client_socket.send(reply)
					else:
						reply = struct.pack(">LLcL", storageid, messageid, b"\x02", count)
						client_socket.send(reply)

						changedFilesTmp = []
						for fileid in changedFiles:
							changedFilesTmp.append(struct.pack("<L", fileid))
						updatefiles = b"".join(changedFilesTmp)

						reply = struct.pack(">LL", storageid, messageid)
						client_socket.send(reply)
						client_socket.send_withlen(updatefiles)

				elif command[0:1] == b"\x06":  # SEND CHECKSUMS

					log.info(f"{clientid}Sending checksums")

					(storageid, messageid) = struct.unpack(">xLL", command)

					if os.path.isfile("files/cache/" + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + "/" + str(storages[storageid].app) + "_" + str(
						storages[storageid].version) + ".manifest"):
						filename = "files/cache/" + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + "/" + str(storages[storageid].app) + ".checksums"
					elif os.path.isfile(self.config["v2manifestdir"] + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + ".manifest"):
						filename = self.config["v2storagedir"] + str(storages[storageid].app) + ".checksums"
					elif os.path.isfile(self.config["manifestdir"] + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + ".manifest"):
						filename = self.config["storagedir"] + str(storages[storageid].app) + ".checksums"
					elif os.path.isdir(self.config["v3manifestdir2"]):
						if os.path.isfile(self.config["v3manifestdir2"] + str(storages[storageid].app) + "_" + str(
								storages[storageid].version) + ".manifest"):
							filename = self.config["v3storagedir2"] + str(storages[storageid].app) + ".checksums"
						else:
							log.error(b"Manifest not found for %s %s " % (app, version))
							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)
							break
					else:
						log.error(b"Checksums not found for %s %s " % (app, version))
						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)
						break
					f = open(filename, "rb")
					file = f.read()
					f.close()

					# hack to rip out old sig, insert new
					file = file[0:-128]
					signature = utilities.encryption.rsa_sign_message(utilities.encryption.network_key, file)

					file = file + signature

					reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(file))

					client_socket.send(reply)

					reply = struct.pack(">LLL", storageid, messageid, len(file))

					client_socket.send(reply + file, False)

				elif command[0:1] == b"\x07":  # SEND DATA

					(storageid, messageid, fileid, filepart, numparts, priority) = struct.unpack(">xLLLLLB", command)

					(chunks, filemode) = storages[storageid].readchunks(fileid, filepart, numparts)

					reply = struct.pack(">LLcLL", storageid, messageid, b"\x00", len(chunks), filemode)

					client_socket.send(reply, False)

					for chunk in chunks:
						reply = struct.pack(">LLL", storageid, messageid, len(chunk))

						client_socket.send(reply, False)

						reply = struct.pack(">LLL", storageid, messageid, len(chunk))

						client_socket.send(reply, False)

						client_socket.send(chunk, False)

				elif command[0:1] == b"\x08":  # INVALID

					log.warning("08 - Invalid Command!")
					client_socket.send(b"\x01")

				else:

					log.warning(f"{binascii.b2a_hex(command[0:1])} - Invalid Command!")
					client_socket.send(b"\x01")

					break

		elif msg == b"\x00\x00\x00\x07":  # \x07 for 2004+

			log.info(f"{clientid}Storage mode entered")

			storagesopen = 0
			storages = {}

			client_socket.send(b"\x01")  # this should just be the handshake

			while True:

				command = client_socket.recv_withlen()

				if command[0:1] == b"\x00":  # BANNER

					if len(command) == 10:
						client_socket.send(b"\x01")
						break
					elif len(command) > 1:
						log.info(b"Banner message: " + binascii.b2a_hex(command))

						if self.config["http_port"] == "steam" or self.config["http_port"] == "0" or globalvars.steamui_ver < 87:
							if self.config["public_ip"] != "0.0.0.0":
								url = "http://" + self.config["public_ip"] + "/platform/banner/random.php"
							else:
								url = "http://" + self.config["http_ip"] + "/platform/banner/random.php"
						else:
							if self.config["public_ip"] != "0.0.0.0":
								url = "http://" + self.config["public_ip"] + ":" + self.config[
									"http_port"] + "/platform/banner/random.php"
							else:
								url = "http://" + self.config["http_ip"] + ":" + self.config[
									"http_port"] + "/platform/banner/random.php"

						reply = struct.pack(">BH", 1, len(url)) + url.encode()

						client_socket.send(reply)
					else:
						client_socket.send(b"")

				elif command[0:1] == b"\xf2":  # SEND CDR - f2 TO DISABLE FOR 2003 TESTING

					blob = cdr_manipulator.fixblobs_configserver()
					checksum = SHA.new(blob).digest()

					if checksum == command[1:]:
						log.info(f"{clientid}Client has matching checksum for secondblob")
						log.debug(f"{clientid}We validate it: {binascii.b2a_hex(command)}")

						client_socket.send(b"\x00\x00\x00\x00")

					else:
						log.info(f"{clientid}Client didn't match our checksum for secondblob")
						log.debug(f"{clientid}Sending new blob: {binascii.b2a_hex(command)}")

						client_socket.send_withlen(blob, False)

				elif command[0:1] == b"\x09" or command[0:1] == b"\x0a" or command[0] == b"\x02":  # REQUEST MANIFEST #09 is used by early clients without a ticket# 02 used by 2003 steam

					if command[0:1] == b"\x0a":
						log.info(f"{clientid}Login packet used")
					# else :
					# log.error(clientid + "Not logged in")

					# reply = struct.pack(">LLc", connid, messageid, b"\x01")
					# client_socket.send(reply)

					# break

					(connid, messageid, app, version) = struct.unpack(">xLLLL", command[0:17])

					log.info(f"{clientid}Opening application %d %d" % (app, version))
					connid = pow(2, 31) + connid

					try:
						s = utilities.storages.Storage(app, self.config["storagedir"], version)
					except Exception:
						log.error("Application not installed! %d %d" % (app, version))

						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)

						break

					storageid = storagesopen
					storagesopen = storagesopen + 1

					storages[storageid] = s
					storages[storageid].app = app
					storages[storageid].version = version

					if str(app) == "3" or str(app) == "7":
						if not os.path.isfile(
								"files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
									version) + ".manifest"):
							if os.path.isfile("files/convert/" + str(app) + "_" + str(version) + ".gcf"):
								log.info("Fixing files in app " + str(app) + " version " + str(version))
								g = open("files/convert/" + str(app) + "_" + str(version) + ".gcf", "rb")
								file = g.read()
								g.close()
								for (search, replace, info) in globalvars.replace_string(islan):
									fulllength = len(search)
									newlength = len(replace)
									missinglength = fulllength - newlength
									if missinglength < 0:
										print(b"WARNING: Replacement text " + replace + b" is too long! Not replaced!")
									elif missinglength == 0:
										file = file.replace(search, replace)
										print(f"Replaced {info}")
									else:
										file = file.replace(search, replace + (b'\x00' * missinglength))
										print(f"Replaced {info}")

								h = open("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf", "wb")
								h.write(file)
								h.close()
								gcf2storage("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")
								sleep(1)
								os.remove("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")

					if os.path.isfile("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
							version) + ".manifest"):
						f = open("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(
							version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a cached depot")
					elif os.path.isfile(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
						f = open(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a v0.2 depot")
					elif os.path.isfile(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest"):
						f = open(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
						log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 depot")
					elif os.path.isdir(self.config["v3manifestdir2"]):
						if os.path.isfile(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest"):
							f = open(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest", "rb")
							log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 extra depot")
						else:
							log.error("Manifest not found for %s %s " % (app, version))
							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)
							break
					else:
						log.error("Manifest not found for %s %s " % (app, version))
						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)
						break
					manifest = f.read()
					f.close()

					manifest_appid = struct.unpack('<L', manifest[4:8])[0]
					manifest_verid = struct.unpack('<L', manifest[8:12])[0]
					log.debug(clientid + ("Manifest ID: %s Version: %s" % (manifest_appid, manifest_verid)))
					if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)):
						log.error("Manifest doesn't match requested file: (%s, %s) (%s, %s)" % (
							app, version, manifest_appid, manifest_verid))

						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)

						break

					globalvars.converting = "0"

					fingerprint = manifest[0x30:0x34]
					oldchecksum = manifest[0x34:0x38]
					manifest = manifest[:0x30] + b"\x00" * 8 + manifest[0x38:]
					checksum = struct.pack("<I", zlib.adler32(manifest, 0))
					manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]

					log.debug(f"Checksum fixed from {binascii.b2a_hex(oldchecksum)} to {binascii.b2a_hex(checksum)}")

					storages[storageid].manifest = manifest

					checksum = struct.unpack("<L", manifest[0x30:0x34])[0]  # FIXED, possible bug source

					reply = struct.pack(">LLcLL", connid, messageid, b"\x00", storageid, checksum)

					client_socket.send(reply, False)

				elif command[0:1] == b"\x01":  # HANDSHAKE

					client_socket.send(b"")
					break

				elif command[0:1] == b"\x03":  # CLOSE STORAGE

					(storageid, messageid) = struct.unpack(">xLL", command)

					del storages[storageid]

					reply = struct.pack(">LLc", storageid, messageid, b"\x00")

					log.info(f"{clientid}Closing down storage %d" % storageid)

					client_socket.send(reply)

				elif command[0:1] == b"\x04":  # SEND MANIFEST

					log.info(f"{clientid}Sending manifest")

					(storageid, messageid) = struct.unpack(">xLL", command)

					manifest = storages[storageid].manifest

					reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(manifest))

					client_socket.send(reply)

					reply = struct.pack(">LLL", storageid, messageid, len(manifest))

					client_socket.send(reply + manifest, False)

				elif command[0:1] == b"\x05":  # SEND UPDATE INFO
					log.info(f"{clientid}Sending app update information")
					(storageid, messageid, oldversion) = struct.unpack(">xLLL", command)
					appid = storages[storageid].app
					version = storages[storageid].version
					log.info("Old GCF version: " + str(appid) + "_" + str(oldversion))
					log.info("New GCF version: " + str(appid) + "_" + str(version))
					manifestNew = Manifest2(appid, version)
					manifestOld = Manifest2(appid, oldversion)

					if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(version) + ".manifest"):
						checksumNew = Checksum3(appid)
					else:
						checksumNew = Checksum2(appid, version)

					if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(oldversion) + ".manifest"):
						checksumOld = Checksum3(appid)
					else:
						checksumOld = Checksum2(appid, version)

					filesOld = {}
					filesNew = {}
					for n in manifestOld.nodes.values():
						if n.fileId != 0xffffffff:
							n.checksum = checksumOld.getchecksums_raw(n.fileId)
							filesOld[n.fullFilename] = n

					for n in manifestNew.nodes.values():
						if n.fileId != 0xffffffff:
							n.checksum = checksumNew.getchecksums_raw(n.fileId)
							filesNew[n.fullFilename] = n

					del manifestNew
					del manifestOld

					changedFiles = []

					for filename in filesOld:
						if filename in filesNew and filesOld[filename].checksum != filesNew[filename].checksum:
							changedFiles.append(filesOld[filename].fileId)
							log.debug("Changed file: " + str(filename) + " : " + str(filesOld[filename].fileId))
						if not filename in filesNew:
							changedFiles.append(filesOld[filename].fileId)
							# if not 0xffffffff in changedFiles:
							# changedFiles.append(0xffffffff)
							log.debug("Deleted file: " + str(filename) + " : " + str(filesOld[filename].fileId))

					for x in range(len(changedFiles)):
						log.debug(changedFiles[x], )

					count = len(changedFiles)
					log.info("Number of changed files: " + str(count))

					if count == 0:
						reply = struct.pack(">LLcL", storageid, messageid, b"\x01", 0)
						client_socket.send(reply)
					else:
						reply = struct.pack(">LLcL", storageid, messageid, b"\x02", count)
						client_socket.send(reply)

						changedFilesTmp = []
						for fileid in changedFiles:
							changedFilesTmp.append(struct.pack("<L", fileid))
						updatefiles = b"".join(changedFilesTmp)

						reply = struct.pack(">LL", storageid, messageid)
						client_socket.send(reply)
						client_socket.send_withlen(updatefiles)

				elif command[0:1] == b"\x06":  # SEND CHECKSUMS

					log.info(f"{clientid}Sending checksums")

					(storageid, messageid) = struct.unpack(">xLL", command)

					if os.path.isfile("files/cache/" + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + "/" + str(storages[storageid].app) + "_" + str(
						storages[storageid].version) + ".manifest"):
						filename = "files/cache/" + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + "/" + str(storages[storageid].app) + ".checksums"
					elif os.path.isfile(self.config["v2manifestdir"] + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + ".manifest"):
						filename = self.config["v2storagedir"] + str(storages[storageid].app) + ".checksums"
					elif os.path.isfile(self.config["manifestdir"] + str(storages[storageid].app) + "_" + str(
							storages[storageid].version) + ".manifest"):
						filename = self.config["storagedir"] + str(storages[storageid].app) + ".checksums"
					elif os.path.isdir(self.config["v3manifestdir2"]):
						if os.path.isfile(self.config["v3manifestdir2"] + str(storages[storageid].app) + "_" + str(
								storages[storageid].version) + ".manifest"):
							filename = self.config["v3storagedir2"] + str(storages[storageid].app) + ".checksums"
						else:
							log.error("Manifest not found for %s %s " % (app, version))
							reply = struct.pack(">LLc", connid, messageid, b"\x01")
							client_socket.send(reply)
							break
					else:
						log.error("Checksums not found for %s %s " % (app, version))
						reply = struct.pack(">LLc", connid, messageid, b"\x01")
						client_socket.send(reply)
						break
					f = open(filename, "rb")
					file = f.read()
					f.close()

					# hack to rip out old sig, insert new
					file = file[0:-128]
					signature = utilities.encryption.rsa_sign_message(utilities.encryption.network_key, file)

					file = file + signature

					reply = struct.pack(">LLcL", storageid, messageid, b"\x00", len(file))

					client_socket.send(reply)

					reply = struct.pack(">LLL", storageid, messageid, len(file))

					client_socket.send(reply + file, False)

				elif command[0:1] == b"\x07":  # SEND DATA

					(storageid, messageid, fileid, filepart, numparts, priority) = struct.unpack(">xLLLLLB", command)

					(chunks, filemode) = storages[storageid].readchunks(fileid, filepart, numparts)

					reply = struct.pack(">LLcLL", storageid, messageid, b"\x00", len(chunks), filemode)

					client_socket.send(reply, False)

					for chunk in chunks:
						reply = struct.pack(">LLL", storageid, messageid, len(chunk))

						client_socket.send(reply, False)

						reply = struct.pack(">LLL", storageid, messageid, len(chunk))

						client_socket.send(reply, False)

						client_socket.send(chunk, False)

				elif command[0:1] == b"\x08":  # INVALID

					log.warning("08 - Invalid Command!")
					client_socket.send(b"\x01")

				else:

					log.warning(f"{binascii.b2a_hex(command[0:1])} - Invalid Command!")
					client_socket.send(b"\x01")

					break

		elif msg == b"\x03\x00\x00\x00":  # UNKNOWN
			log.info(f"{clientid}Unknown mode entered")
			client_socket.send(b"\x00")

		else:
			log.warning(f"Invalid Command: {binascii.b2a_hex(msg)}")

		client_socket.close()
		log.info(f"{clientid}Disconnected from Content Server")

	def parse_manifest_files(self, contentserver_info):

		# Define the locations to search for '.manifest' files
		locations = ['files/cache/', self.config["v2manifestdir"], self.config["manifestdir"],
					 self.config["v3manifestdir2"]]
		app_buffer = ""
		for location in locations:
			for file_name in os.listdir(location):
				if file_name.endswith('.manifest'):
					# Extract app ID and version from the file name
					app_id, version = file_name.split('_')
					version = version.rstrip('.manifest')
					# for appid, version in self.applist:
					# print("appid:", app_id)
					# print("version:", version)
					# Append app ID and version to app_list in this format
					app_buffer += str(app_id) + "\x00" + str(version) + "\x00\x00"
					app_list.append((app_id, version))
		return app_buffer