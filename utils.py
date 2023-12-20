import binascii
import filecmp
import logging
import os
import random
import shutil
import string
import subprocess
import sys
import time
import requests
from future.utils import old_div
from tqdm import tqdm
from collections import Counter
from datetime import datetime, timedelta

import globalvars
from config import get_config as read_config
from utilities import cafe_neutering, neuter, packages
from utilities.converter import convertgcf
from utilities.database import ccdb
from utilities.packages import Package


config = read_config( )
log = logging.getLogger('UTILS')


def to_hex_8bit(value):
	return bytes.fromhex(format(value, '02x'))


def to_hex_16bit(value):
	return bytes.fromhex(format(value, '04x'))


def to_hex_32bit(value):
	return bytes.fromhex(format(value, '08x'))


def hex_to_decimal(hex_string):
	return int(hex_string, 16)


def hex_to_string(hex_string):
	bytes_object = bytes.fromhex(hex_string)
	return bytes_object.decode("ASCII")


def hex_to_bytes(hex_string):
	return bytes.fromhex(hex_string)


def decodeIP(string):
	(oct1, oct2, oct3, oct4, port) = struct.unpack("<BBBBH", string)
	ip = "%d.%d.%d.%d" % (oct1, oct2, oct3, oct4)
	return ip, port


def encodeIP(ip_port):
	ip, port = ip_port  # Unpacking the tuple
	if isinstance(port, str):
		port = int(port)
	if isinstance(ip, str):
		ip = ip.encode("latin-1")
	octets = ip.split(b".")
	packed_string = struct.pack("<BBBBH", int(octets[0]), int(octets[1]), int(octets[2]), int(octets[3]), port)
	return packed_string


def readfile_beta(fileid, offset, length, index_data, dat_file_handle, net_type):
	# Load the index
	# with open(index_file, 'rb') as f:
	#    index_data = pickle.load(f)

	# Get file information from the index
	if fileid not in index_data:
		print("Error: File number not found in index.")
		return None

	file_info = index_data[fileid]
	# print(file_info)
	dat_offset, dat_size = file_info['offset'], file_info['length']

	oldstringlist1 = (
		b'"hlmaster.valvesoftware.com:27010"', b'"half-life.east.won.net:27010"',
		b'"gridmaster.valvesoftware.com:27012"',
		b'"half-life.west.won.net:27010"', b'"207.173.177.10:27010"')
	oldstringlist2 = (b'"tracker.valvesoftware.com:1200"', b'"tracker.valvesoftware.com:1200"')
	oldstringlist3 = (
		b'207.173.177.10:7002', b'half-life.speakeasy-nyc.hlauth.net:27012',
		b'half-life.speakeasy-sea.hlauth.net:27012',
		b'half-life.speakeasy-chi.hlauth.net:27012')
	oldstringlist4 = (b'207.173.177.10:27010', b'207.173.177.10:27010')

	if net_type == "external":
		newstring1 = b'"' + config["public_ip"].encode('latin-1') + b':27010"'
	else:
		newstring1 = b'"' + config["server_ip"].encode('latin-1') + b':27010"'
	if net_type == "external":
		newstring2 = b'"' + config["public_ip"].encode('latin-1') + b':1200"'
	else:
		newstring2 = b'"' + config["tracker_ip"].encode('latin-1') + b':1200"'
	if net_type == "external":
		newstring3 = config["public_ip"].encode('latin-1') + b':' + config["validation_port"].encode('latin-1')
	else:
		newstring3 = config["server_ip"].encode('latin-1') + b':' + config["validation_port"].encode('latin-1')
	if net_type == "external":
		newstring4 = config["public_ip"].encode('latin-1') + b':27010'
	else:
		newstring4 = config["server_ip"].encode('latin-1') + b':27010'

	# Extract and decompress the file from the .dat file
	# with open(dat_file, 'rb') as f:
	# f.seek(dat_offset + offset)
	dat_file_handle.seek(dat_offset + offset)
	decompressed_data = dat_file_handle.read(length)
	for oldstring1 in oldstringlist1:
		if oldstring1 in decompressed_data:
			stringlen_diff1 = len(oldstring1) - len(newstring1)
			replacestring1 = newstring1 + (b"\x00" * stringlen_diff1)
			decompressed_data = decompressed_data.replace(oldstring1, replacestring1)
	for oldstring2 in oldstringlist2:
		if oldstring2 in decompressed_data:
			stringlen_diff2 = len(oldstring2) - len(newstring2)
			replacestring2 = newstring2 + (b"\x00" * stringlen_diff2)
			decompressed_data = decompressed_data.replace(oldstring2, replacestring2)
	for oldstring3 in oldstringlist3:
		if oldstring3 in decompressed_data:
			stringlen_diff3 = len(oldstring3) - len(newstring3)
			replacestring3 = newstring3 + (b" " * stringlen_diff3)
			decompressed_data = decompressed_data.replace(oldstring3, replacestring3)
	for oldstring4 in oldstringlist4:
		if oldstring4 in decompressed_data:
			stringlen_diff4 = len(oldstring4) - len(newstring4)
			replacestring4 = newstring4 + (b" " * stringlen_diff4)
			decompressed_data = decompressed_data.replace(oldstring4, replacestring4)
		# decompressed_data = zlib.decompress(compressed_data)

	# print(len(decompressed_data[offset:offset + length]))
	# print(len(compressed_data[offset:offset + length]))

	# with open(str(FILE_COUNT) + ".file", "wb") as f:
	#    f.write(decompressed_data)

	return decompressed_data  # [offset:offset + length]


def get_current_datetime():
	# Get the current datetime object
	current_datetime = datetime.now( )
	# Format the datetime object as "mm/dd/yyyy hr:mn:sec"
	formatted_datetime = current_datetime.strftime("%m/%d/%Y %H:%M:%S")
	return formatted_datetime


def add_100yrs(dt):
	# Add 100 years to the datetime object
	# 365.25 days per year on average (considering leap years)
	date_format = "%m/%d/%Y %H:%M:%S"
	# Convert the string to a datetime object
	datetime_object = datetime.strptime(dt, date_format)
	newdatetime = datetime_object + timedelta(days=36525)

	return str(newdatetime.strftime("%m/%d/%Y %H:%M:%S"))


def steamtime_to_datetime(raw_bytes):
	steam_time = struct.unpack("<Q", raw_bytes)[0]
	unix_time = old_div(steam_time, 1000000) - 62135596800
	dt_object = datetime.utcfromtimestamp(unix_time)
	formatted_datetime = dt_object.strftime('%m/%d/%Y %H:%M:%S')
	return formatted_datetime


def datetime_to_steamtime(formatted_datetime):
	dt_object = datetime.strptime(formatted_datetime, '%m/%d/%Y %H:%M:%S')
	unix_time = int((dt_object - datetime(1970, 1, 1)).total_seconds( ))
	steam_time = (unix_time + 62135596800) * 1000000
	raw_bytes = struct.pack("<Q", steam_time)

	# Convert the hexadecimal string to a byte array
	byte_array = bytearray(binascii.unhexlify(raw_bytes))

	return byte_array  # str(b'\x00\x00\x00\x00\x00\x00\x00\x00')


def steamtime_to_unixtime(steamtime_bin):
	steamtime = struct.unpack("<Q", steamtime_bin)[0]
	unixtime = steamtime / 1000000 - 62135596800
	return unixtime


def unixtime_to_steamtime(unixtime):
	steamtime = int((unixtime + 62135596800) * 1000000)  # Ensure steamtime is an integer
	steamtime_bin = struct.pack("<Q", steamtime)
	return steamtime_bin


def get_nanoseconds_since_time0():
	before_time0 = 62135596800
	current = int(time.time( ))
	now = current + before_time0
	nano = 1000000
	now *= nano
	return now


def cmp(a, b):
	return (a > b) - (a < b)


def sortkey(x):
	if len(x) == 4 and x[2] == 0:
		return x[::-1]
	else:
		return x


def sortfunc(x, y):
	if len(x) == 4 and x[2] == 0:
		if len(y) == 4 and y[2] == 0:
			numx = struct.unpack("<I", x)[0]
			numy = struct.unpack("<I", y)[0]
			return cmp(numx, numy)
		else:
			return -1
	else:
		if len(y) == 4 and y[2] == 0:
			return 1
		else:
			return cmp(x, y)


def formatstring(text):
	if len(text) == 4 and text[2] == b"\x00":
		return (b"'\\x%02x\\x%02x\\x%02x\\x%02x'") % (ord(text[0]), ord(text[1]), ord(text[2]), ord(text[3]))
	else:
		return repr(text)


def autoupdate(arguments):
	if not config["emu_auto_update"].lower() == "false":
		autoupdate(sys.argv[0])

		if arguments.endswith("emulator.exe"):
			try:
				if os.path.isfile("emulatorTmp.exe"):
					os.remove("emulatorTmp.exe")
				if os.path.isfile("emulatorNew.exe"):
					os.remove("emulatorNew.exe")
				# if clear_config == True :
					# print("Config change detected, flushing cache...")
					# shutil.rmtree("files/cache")
					# os.mkdir("files/cache")
					# shutil.copy("emulator.ini", "files/cache/emulator.ini.cache")
					# print
				if config["uat"] == "1":
					#url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update-test/main/version"
					url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update/main/version"
				else:
					url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update/main/version"
				resp = requests.get(url)
				online_ver = resp.text

				for file in os.listdir("."):
					if file.endswith(".mst") or file.endswith(".out"):
						emu_ver = file[7:-4]
					elif file.endswith(".pkg") or file.endswith(".srv"):
						os.remove(file)

				f = open("server_0.mst", "w")
				f.close()

				if not online_ver == globalvars.emu_ver or not os.path.isfile("server_" + online_ver + ".out"):
					shutil.copy("emulator.exe", "emulatorTmp.exe")
					print("Update found " + globalvars.emu_ver + " -> " + online_ver + ", downloading...")
					if config["uat"] == "1":
						#url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update-test/main/server_" + online_ver + ".pkg"
						url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update/main/server_" + online_ver + ".pkg"
					else:
						url = "https://raw.githubusercontent.com/real-pmein1/stmemu-update/main/server_" + online_ver + ".pkg"
					# Streaming, so we can iterate over the response.
					response = requests.get(url, stream=True)
					total_size_in_bytes = int(response.headers.get('content-length', 0))
					block_size = 1024  # 1 Kilobyte
					progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True, ncols=80)
					with open('server_' + online_ver + '.pkg', 'wb') as file:
						for data in response.iter_content(block_size):
							progress_bar.update(len(data))
							file.write(data)
					progress_bar.close( )
					if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
						print("ERROR, something went wrong")

					packages.package_unpack2('server_' + online_ver + '.pkg', ".", online_ver)

					for file in os.listdir("."):
						if file.endswith(".mst") and file != "server_" + online_ver + ".mst" :
							os.remove(file)
						elif file.endswith(".out"):
							os.remove(file)
						elif file.endswith(".pkg"):
							os.remove(file)
					subprocess.Popen("emulatorTmp.exe")
					sys.exit(0)

			except Exception as e:
				globalvars.update_exception1 = e
			finally:
				if os.path.isfile("server_0.mst"): os.remove("server_0.mst")
		elif arguments.endswith("emulatorTmp.exe") and not os.path.isfile("emulatorNew.exe"):
			print("WAITING...")
			try:

				os.remove("emulator.exe")
				shutil.copy("emulatorTmp.exe", "emulator.exe")
				subprocess.Popen("emulator.exe")
				sys.exit(0)

			except Exception as e:
				globalvars.update_exception2 = e
		else:
			print("WAITING...")
			try:
				os.remove("emulator.exe")
				shutil.copy("emulatorNew.exe", "emulator.exe")
				subprocess.Popen("emulator.exe")
				sys.exit(0)

			except Exception as e:
				globalvars.update_exception2 = e
	else:
		print("Skipping checking for updates (ini override)")
		return


import socket
import struct


def get_external_ip(stun_server='stun.ekiga.net', stun_port=3478):
	# STUN server request
	stun_request = b'\x00\x01' + b'\x00\x00' + b'\x21\x12\xA4\x42' + b'\x00' * 12

	# Create a UDP socket
	with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
		sock.settimeout(2)

		# Resolve STUN server IP
		server_address = (socket.gethostbyname(stun_server), stun_port)

		try:
			# Send request to STUN server
			sock.sendto(stun_request, server_address)

			# Receive response
			data, _ = sock.recvfrom(1024)

			# Check for a valid response length
			if len(data) < 20:
				return 'Invalid response'

			# Check if it's a binding response message (success)
			msg_type, msg_len = struct.unpack_from('!HH', data, 0)
			if msg_type == 0x0101 and msg_len > 0:
				# Parse the response to get the external IP and port
				index = 20  # Start after header
				while index < len(data):
					attr_type, attr_len = struct.unpack_from('!HH', data, index)
					# Check for MappedAddress (0x0001) attribute
					if attr_type == 0x0001 and attr_len >= 8:
						# Unpack IP and convert to dotted-decimal notation
						port, ip = struct.unpack_from('!xH4s', data[1:], index + 4)
						ip = socket.inet_ntoa(ip)
						print(f"Public IP: {ip}")
						return ip
					index += 4 + attr_len
		except socket.error:
			pass
	return 'Unable to determine external IP'


def is_valid_ip(ip_address):
	"""Checks if the given IP address is valid."""
	try:
		socket.inet_aton(ip_address)
		return Counter(ip_address)['.'] == 3 and all(char.isdigit( ) or char == '.' for char in ip_address)
	except:
		return False


def check_ip_and_exit(ip_address, ip_type):
	"""Checks an IP address, logs error and exits if invalid."""
	if ip_address != "0.0.0.0" and not is_valid_ip(ip_address):
		log.error(f"ERROR! The {ip_type} ip is malformed, currently {ip_address}")
		input("Press Enter to exit...")
		quit( )


def checkip():
	check_ip_and_exit(config["server_ip"], "server")
	check_ip_and_exit(config["public_ip"], "public")
	check_ip_and_exit(config["community_ip"], "community")


def setserverip():
	# Define the IP prefixes and their corresponding network strings
	#ip_prefixes = {
	#    "10."     :"('10.",
	#    **{"172." + str(i) + ".":"('172." + str(i) + "." for i in range(16, 32)},
	#    "192.168.":"('192.168."
	#}

	# Check and set the server network based on IP prefixes
	#for prefix, network in ip_prefixes.items( ):
	#    if config["server_ip"].startswith(prefix):
	#        globalvars.servernet = network
	#        break

	# Determine the length for formatting
	iplen = max(len(config["server_ip"]), len(config["public_ip"]))

	# Printing the information
	print(("*" * 11) + ("*" * iplen))
	print(f"Server IP: {config['server_ip']}")
	if config["public_ip"] != "0.0.0.0":
		globalvars.public_ip = config['public_ip']
		globalvars.public_ip_b = globalvars.public_ip.encode("latin-1")
		print(f"Public IP: {globalvars.public_ip}")

	print(("*" * 11) + ("*" * iplen))
	print("")


def initialize(log):
	# Initial loading for ccdb for steam.exe neutering and palcement.
	firstblob_eval = ccdb.load_ccdb( )

	for filename in os.listdir("files/cache/") :
		if globalvars.record_ver == 1 and "SteamUI_" in filename :
			os.remove("files/cache/" + filename)
			break
		elif globalvars.record_ver != 1 and "PLATFORM_" in filename :
			os.remove("files/cache/" + filename)
			break

	if os.path.isdir("files/cache/internal") :
		for filename in os.listdir("files/cache/internal/") :
			if globalvars.record_ver == 1 and "SteamUI_" in filename :
				os.remove("files/cache/internal/" + filename)
				break
			elif globalvars.record_ver != 1 and "PLATFORM_" in filename :
				os.remove("files/cache/internal/" + filename)
				break

	if os.path.isdir("files/cache/external") :
		for filename in os.listdir("files/cache/external/") :
			if globalvars.record_ver == 1 and "SteamUI_" in filename :
				os.remove("files/cache/external/" + filename)
				break
			elif globalvars.record_ver != 1 and "PLATFORM_" in filename :
				os.remove("files/cache/external/" + filename)
				break

	if config["http_port"].startswith(":"):
		print(config["http_port"])
		linenum = 0
		with open("emulator.ini", "r") as f:
			data = f.readlines( )
		for line in data:
			if line.startswith("http_port"):
				break
			linenum += 1
		data[linenum] = "http_port=" + config["http_port"][1:] + "\n"
		with open("emulator.ini", "w") as g:
			g.writelines(data)
		if os.path.isfile("files/cache/emulator.ini.cache"):
			os.remove("files/cache/emulator.ini.cache")
		shutil.copy("emulator.exe", "emulatorTmp.exe")
		subprocess.Popen("emulatorTmp.exe")
		sys.exit(0)

	if not os.path.isfile("files/cache/emulator.ini.cache"):
		print("Config change detected, flushing cache...")
		shutil.rmtree("files/cache")
		os.mkdir("files/cache")
		shutil.copy("emulator.ini", "files/cache/emulator.ini.cache")
		print( )
	else:
		try:
			if filecmp.cmp("emulator.ini", "files/cache/emulator.ini.cache"):  # false = different, true = same
				a = 0
			else:
				print("Config change detected, flushing cache...")
				shutil.rmtree("files/cache")
				os.mkdir("files/cache")
				shutil.copy("emulator.ini", "files/cache/emulator.ini.cache")
				print( )
		except:
			print("Config change detected, flushing cache...")
			shutil.rmtree("files/cache")
			os.mkdir("files/cache")
			shutil.copy("emulator.ini", "files/cache/emulator.ini.cache")
			print( )
	if config["auto_public_ip"] == "true":
		globalvars.public_ip = get_external_ip( )
		globalvars.public_ip_b = globalvars.public_ip.encode("latin-1")
	else:
		checkip( )
		setserverip( )


def finalinitialize(log):
	#  modify the steam and hlsupdatetool binary files
	if globalvars.record_ver == 0:
		# beta 1 v0
		f = open(config["packagedir"] + "betav1/Steam_" + str(globalvars.steam_ver) + ".pkg", "rb")
	elif globalvars.record_ver == 1:
		f = open(config["packagedir"] + "betav2/Steam_" + str(globalvars.steam_ver) + ".pkg", "rb")
	else:
		f = open(config["packagedir"] + "Steam_" + str(globalvars.steam_ver) + ".pkg", "rb")
	pkg = Package(f.read( ))
	f.close( )

	if config["reset_clears_client"].lower() == "true":
		if config["public_ip"] != "0.0.0.0" and not os.path.isdir("client/wan"):
			shutil.rmtree("client")
		elif config["public_ip"] == "0.0.0.0" and os.path.isdir("client/wan"):
			shutil.rmtree("client")

	try:
		os.mkdir("client")
		os.mkdir("client/lan")
		os.mkdir("client/wan")
	except:
		pass

	file = pkg.get_file(b"SteamNew.exe")
	file2 = pkg.get_file(b"SteamNew.exe")


	if config["public_ip"] != "0.0.0.0":

		if not os.path.isdir("client/lan"):
			os.mkdir("client/lan")
		if not os.path.isdir("client/wan"):
			os.mkdir("client/wan")

		file = neuter.neuter_file(file, config["public_ip"], config["dir_server_port"], b"SteamNew.exe", False)
		file2 = neuter.neuter_file(file2, config["server_ip"], config["dir_server_port"], b"SteamNewLAN.exe", True)

		f = open("client/wan/Steam.exe", "wb")
		g = open("client/lan/Steam.exe", "wb")

		f.write(file)
		g.write(file2)

		f.close( )
		g.close( )
	else:

		file = neuter.neuter_file(file, config["server_ip"], config["dir_server_port"], b"SteamNew.exe", True)
		# file2 = neuter_file(file, config["public_ip"], config["dir_server_port"], b"SteamNew.exe", False)

		f = open("client/Steam.exe", "wb")
		# g = open("client/lan/Steam.exe", "wb")

		f.write(file)
		# g.write(file2)

		f.close( )
		# g.close( )

	if globalvars.record_ver != 0 and config["hldsupkg"] != "":
		if globalvars.record_ver == 1 :
			g = open(config["packagedir"] + "betav2/" + config["hldsupkg"], "rb")
		else:
			g = open(config["packagedir"] + config["hldsupkg"], "rb")
		pkg = Package(g.read( ))
		g.close( )
		file = pkg.get_file(b"HldsUpdateToolNew.exe")
		file = neuter.neuter_file(file, config["public_ip"], config["dir_server_port"], b"HldsUpdateToolNew.exe", False)
		file2 = neuter.neuter_file(file, config["server_ip"], config["dir_server_port"], b"HldsUpdateToolNew.exe", True)

		g = open("client/wan/HldsUpdateTool.exe", "wb")
		f = open("client/lan/HldsUpdateTool.exe", "wb")

		g.write(file)
		f.write(file2)

		g.close( )
		f.close( )

	# TODO NEED TO DEPRECATE THIS IN FAVOR OF PROTOCOL VERSIONING
	if globalvars.steamui_ver < 61:  # guessing steamui version when steam client interface v2 changed to v3
		globalvars.tgt_version = "1"
	else:
		globalvars.tgt_version = "2"  # config file states 2 as default

	if globalvars.steamui_ver < 122:
		if os.path.isfile("files/cafe/Steam.dll"):
			log.info("Cafe files found")
			cafe_neutering.process_cafe_files(
					"files/cafe/Steam.dll",
					"files/cafe/CASpackage.zip",
					"client/cafe_server/CASpackageWAN.zip",
					"client/cafe_server/CASpackageLAN.zip",
					"files/cafe/README.txt",
					"client/Steam.exe",
					config
			)

	if config["use_sdk"] == "1":
		with open("files/pkg_add/steam/Steam.cfg", "w") as h:
			h.write('SdkContentServerAdrs = "' + config["sdk_ip"] + ':' + config["sdk_port"] + '"\n')
		if os.path.isfile("files/cache/Steam_" + str(globalvars.steam_ver) + ".pkg"):
			os.remove("files/cache/Steam_" + str(globalvars.steam_ver) + ".pkg")
	else:
		if os.path.isfile("files/pkg_add/steam/Steam.cfg"):
			os.remove("files/cache/Steam_" + str(globalvars.steam_ver) + ".pkg")
			os.remove("files/pkg_add/steam/Steam.cfg")

	if os.path.isfile("Steam.exe"):
		os.remove("Steam.exe")
	if os.path.isfile("HldsUpdateTool.exe"):
		os.remove("HldsUpdateTool.exe")
	if os.path.isfile("log.txt"):
		os.remove("log.txt")
	if os.path.isfile("library.zip"):
		os.remove("library.zip")
	if os.path.isfile("MSVCR71.dll"):
		os.remove("MSVCR71.dll")
	if os.path.isfile("python24.dll"):
		os.remove("python24.dll")
	if os.path.isfile("python27.dll"):
		os.remove("python27.dll")
	if os.path.isfile("Steam.cfg"):
		os.remove("Steam.cfg")
	if os.path.isfile("w9xpopen.exe"):
		os.remove("w9xpopen.exe")
	# if os.path.isfile("submanager.exe") :
	#    os.remove("submanager.exe")

	if os.path.isfile("files/users.txt"):
		users = {}  # REMOVE LEGACY USERS
		f = open("files/users.txt")
		for line in f.readlines( ):
			if line[-1:] == "\n":
				line = line[:-1]
			if line.find(":") != -1:
				(user, password) = line.split(":")
				users[user] = user
		f.close( )
		for user in users:
			if os.path.isfile("files/users/" + user + ".py"):
				os.rename("files/users/" + user + ".py", "files/users/" + user + ".legacy")
		os.rename("files/users.txt", "files/users.off")


def generate_password():
	"""
	Generate a random password consisting of letters (uppercase and lowercase),
	digits, and punctuation characters.

	Returns:
		str: The generated password.
	"""
	characters = string.ascii_letters + string.digits + string.punctuation
	password = ''.join(random.choice(characters) for _ in range(16))
	return password


def check_peerpassword():
	try:
		# Check if there is a peer password, if not it'll generate one
		if "peer_password" in config and config["peer_password"]:
			# The peer_password is present and not empty
			globalvars.peer_password = config["peer_password"]
			return 0
		else:
			# The peer_password is missing or empty
			# Generate a new password
			globalvars.peer_password = generate_password( )

			# Save the new password to the config file
			config.save_config_value("peer_password", globalvars.peer_password)
			return 1
	except Exception as e:
		print(f"An error occurred while checking/setting peer password: {e}")
		return -1


def flush_cache():
	try:
		mod_date_emu = os.path.getmtime("emulator.exe")
	except:
		mod_date_emu = 0
	try:
		mod_date_cach = os.path.getmtime("files/cache/emulator.ini.cache")
	except:
		mod_date_cach = 0

	if (mod_date_cach < mod_date_emu) and globalvars.clear_config is True:
		print("Config change detected, flushing cache...")
		try:
			shutil.rmtree("files/cache")
		except:
			pass


def parent_initializer():
	log.info("---Starting Initialization---")


	globalvars.cs_region = config["cs_region"]
	globalvars.dir_ismaster = config["dir_ismaster"]
	globalvars.server_ip = config["server_ip"]
	globalvars.server_ip_b = globalvars.server_ip.encode("latin-1")
	globalvars.public_ip = config["public_ip"]

	initialize(log)

	if not globalvars.update_exception1 == "":
		log.debug("Update1 error: " + str(globalvars.update_exception1))
	if not globalvars.update_exception2 == "":
		log.debug("Update2 error: " + str(globalvars.update_exception2))

	finalinitialize(log)

	log.info("Checking for gcf files to convert...")
	if config["show_convert_bar"].lower() == "true":
		globalvars.hide_convert_prints = True

	convertgcf()

	globalvars.hide_convert_prints = False

	# TODO BEN, FINISH BETA 1 NEUTERING
	# neuter.replace_bytes_in_file("steam_v0.exe")
	# neuter.replace_bytes_in_file("steam_v1.exe")

	log.info("---Initialization Complete---")
	print()

	# check for a peer_password, otherwise generate one
	return check_peerpassword()