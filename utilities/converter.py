import binascii
import logging
import os
import struct

import globalvars
from config import read_config
from gcf_to_storage import gcf2storage

config = read_config()

def convertgcf() :
	log = logging.getLogger("converter")

	if config["public_ip"] == "0.0.0.0":
		islan = True
		server_ip = config["server_ip"].encode('latin-1')
	else:
		islan = False
		server_ip = config["public_ip"].encode('latin-1')
	dirsrv_port = config["dir_server_port"].encode('latin-1')

	# makeenc = Manifest()
	# makeenc.make_encrypted("files/convert/206_1.manifest")
	# makeenc.make_encrypted("files/convert/207_1.manifest")
	# makeenc.make_encrypted("files/convert/208_1.manifest")
	# makeenc.make_encrypted("files/convert/221_0.manifest")
	# makeenc.make_encrypted("files/convert/281_0.manifest")

	for filename in os.listdir("files/convert/") :
		if str(filename.endswith(".gcf")) :
			# dirname = filename[0:-4]
			with open("files/convert/" + filename, "rb") as g:
				h = g.read(20)

			depotid = struct.unpack("<L", h[12:16])[0]
			versionid = struct.unpack("<L", h[16:20])[0]
			dirname = str(depotid) + "_" + str(versionid)

			if not os.path.isfile("files/cache/" + dirname + "/" + dirname + ".manifest") :
				log.info("Found " + filename + " to convert")
				log.info("Neutering Valve strings...")
				log.debug("****************************************")
				g = open("files/convert/" + filename, "rb")
				file = g.read()
				g.close()
				searchip_1 = [
				(b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038", "Replaced directory server IP group 1"),
				(b"207.173.177.11:27030 207.173.177.12:27030", "Replaced directory server IP group 5")
				]

				if not islan:
					ip = server_ip + b":" + dirsrv_port + b" " + server_ip + b":" + dirsrv_port + b" "
				else :
					ip = server_ip + b":" + dirsrv_port + b" "
				for search, message in searchip_1:
					searchlength = len(search)
					ips = ip * (searchlength // len(ip))
					replace = ips.ljust(searchlength, b'\x00')
					if file.find(search) != -1:
						file = file.replace(search, replace)
						log.debug(message)

				searchip_2 = [
				(b"hlmaster1.hlauth.net:27010", 	server_ip +  b":27010", "Replaced default HL Master server DNS"),
				(b"207.173.177.11:27010", 			server_ip +  b":27010", "Replaced default HL Master server IP 1"),
				(b"207.173.177.12:27010",			server_ip +  b":27010", "Replaced default HL Master server IP 2"),
				(b"207.173.177.11:27011", 			server_ip +  b":27011", "Replaced default HL2 Master server IP 1"),
				(b"207.173.177.12:27011", 			server_ip +  b":27011", "Replaced default HL2 Master server IP 2"),
				(b"tracker.valvesoftware.com:1200", server_ip +  b":1200", "Replaced Tracker Chat server DNS"),
				(b'"207.173.177.42:1200"',  b'\"' + server_ip +  b':1200\"', "Replaced Tracker Chat server 1"),
				(b'"207.173.177.43:1200"',  b'\"' + server_ip +  b':1200\"', "Replaced Tracker Chat server 2"),
				(b'"207.173.177.44:1200"',  b'\"' + server_ip +  b':1200\"', "Replaced Tracker Chat server 3"),
				(b'"207.173.177.45:1200"',  b'\"' + server_ip +  b':1200\"', "Replaced Tracker Chat server 4")
				]

				for search, ip, message in searchip_2:
					search_length = len(search)
					replace_length = len(ip)

					# Calculate how many bytes need to be added to make the lengths match
					padding_length = search_length - replace_length

					# If padding is required, add \x00 bytes to the replacement string
					if padding_length > 0:
						replace = ip + (b'\x00' * padding_length)
					else:
						replace = ip

					# Perform the replacement
					if file.find(search) != -1:
						file = file.replace(search, replace)
						log.debug(message)

				for ip in globalvars.extraips + globalvars.ip_addresses:
					file = ip_replacer(file,filename,ip,log,server_ip)

				if server_ip != "127.0.0.1" :
					for ip in globalvars.loopback_ips:
						file = ip_replacer(file,filename,ip,log,server_ip)

				for (search, replace, info) in globalvars.replace_string(islan):
					file = find_replace(file,info,log,replace,search, False)

				if config["http_port"] != "steam":
					for (search, replace, info) in globalvars.replace_string_name_space(islan) :
						file = find_replace(file,info,log,replace,search, True)

					for (search, replace, info) in globalvars.replace_string_name(islan) :
						file = find_replace(file,info,log,replace,search, False)

				search = binascii.a2b_hex("2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
				replace = binascii.a2b_hex("2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
				file = file.replace(search, replace)
				log.debug("Replaced CC expiry date field")

				h = open("files/temp/" + dirname + ".neutered.gcf", "wb")
				h.write(file)
				h.close()
				log.info("Converting fixed gcf to cache...")
				gcf2storage("files/temp/" + dirname + ".neutered.gcf")
				os.remove("files/temp/" + dirname + ".neutered.gcf")
				log.debug("****************************************")
def ip_replacer(file, filename, ip, log, server_ip):
	loc = file.find(ip)
	if loc != -1:
		# Calculate the number of padding bytes needed
		padding_needed = len(ip) - len(server_ip)
		if padding_needed > 0:
			# Pad the replacement IP with '\x00' only if padding is needed
			replace_ip = server_ip + (b'\x00' * padding_needed)
		else:
			# No padding needed, use server_ip as is
			replace_ip = server_ip

		# Replace the IP in the file
		file = file[:loc] + replace_ip + file[loc + len(ip):]
		log.debug(f"{filename}: Found and replaced IP {ip} at location {loc:08x}")

	return file


def find_replace(file, info, log, replace, search, null_padded=False):
	search_length = len(search)
	replace_length = len(replace)

	# Decide the padding character based on the 'null_padded' flag
	padding_char = b'\x00' if null_padded else b'\x20'

	# Use 'ljust' to ensure 'replace' is of the same length as 'search'
	# This adds the right padding character to match the lengths
	padded_replace = replace.ljust(search_length, padding_char)

	if replace_length > search_length:
		log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
	else:
		file = file.replace(search, padded_replace)
		log.debug(f"Replaced {info} {search} with {padded_replace}")

	return file