import binascii
import logging
import os
import struct
import threading
import time
import concurrent.futures

import globalvars
from config import get_config as read_config
from gcf_to_storage import gcf2storage

config = read_config( )

def replace_ip_addresses(file, log, config, event):
	ip_replacements = [
		(b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038", "dir_server_port", "Replaced directory server IP group 1"),
		(b"207.173.177.11:27030 207.173.177.12:27030", "dir_server_port", "Replaced directory server IP group 5"),
		(b"hlmaster1.hlauth.net:27010", "27010", "Replaced default HL Master server DNS"),
		(b"207.173.177.11:27010", "27010", "Replaced default HL Master server IP 1"),
		(b"207.173.177.12:27010", "27010", "Replaced default HL Master server IP 2"),
		(b"207.173.177.11:27011", "27011", "Replaced default HL2 Master server IP 1"),
		(b"207.173.177.12:27011", "27011", "Replaced default HL2 Master server IP 2"),
		(b"tracker.valvesoftware.com:1200", "1200", "Replaced Tracker Chat server DNS"),
		(b'"207.173.177.42:1200"', "1200", "Replaced Tracker Chat server 1"),
		(b'"207.173.177.43:1200"', "1200", "Replaced Tracker Chat server 2"),
		(b'"207.173.177.44:1200"', "1200", "Replaced Tracker Chat server 3"),
		(b'"207.173.177.45:1200"', "1200", "Replaced Tracker Chat server 4")
	]

	for search, port, message in ip_replacements:
		ip = (config["public_ip"] if config["public_ip"] != "0.0.0.0" else config["server_ip"]) + f":{port}"
		search_length = len(search)
		ip_length = len(ip)
		num_to_replace = search_length // ip_length
		ips = (ip + " ") * num_to_replace
		replace = ips.encode('latin-1') + (b'\x00' * (search_length - len(ips)))
		loc = file.find(search)
		if loc != -1:
			file = file.replace(search, replace)
			log.debug(message)
			log.debug(f"Replaced IP {ip} at location {loc:08x} with {replace}")
			verify_replacement(file, loc, replace, log)

	# CC expiry date field replacement
	search = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
	replace = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
	loc = file.find(search)
	file = file.replace(search, replace)
	log.debug("Replaced CC expiry date field")
	log.debug(f"Replaced CC expiry date field at location {loc:08x}")
	verify_replacement(file, loc, replace, log)
	event.set()


def parallel_process_file(file, log, config, origsize, replace_strings, replace_strings_name):
	# Initialize events for synchronization
	event1 = threading.Event()
	event2 = threading.Event()
	event3 = threading.Event()
	event4 = threading.Event()
	event5 = threading.Event()
	if config["public_ip"] != "0.0.0.0" :
		server_ip = config["public_ip"]
	else:
		server_ip = config["server_ip"]
	server_ip = server_ip.encode("latin-1")
	# Start threads
	thread1 = threading.Thread(target=find_replace1, args=(file, log, replace_strings, event1))
	thread2 = threading.Thread(target=find_replace2, args=(file, log, origsize, replace_strings_name, event2))
	thread3 = threading.Thread(target=replace_ip_addresses, args=(file, log, config, event3))
	thread4 = threading.Thread(target=replace_ips_combined, args=(file, log, config, origsize, event4))
	thread5 = threading.Thread(target=replace_loopback_ips, args=(file,log,server_ip, event5))
	thread1.start()
	thread2.start()
	thread3.start()
	thread4.start()
	thread5.start()

	# Wait for all threads to complete
	event1.wait()
	event2.wait()
	event3.wait()
	event4.wait()
	event5.wait()

	# Return the modified file
	return file


def convertgcf() :
	log = logging.getLogger("converters")

	for filename in os.listdir("files/convert/") :
		if str(filename.endswith(".gcf")) :
			# dirname = filename[0:-4]
			with open("files/convert/" + filename, "rb") as g :
				h = g.read(20)

			depotid = struct.unpack("<L", h[12 :16])[0]
			versionid = struct.unpack("<L", h[16 :20])[0]

			dirname = str(depotid) + "_" + str(versionid)
			if not os.path.isfile("files/cache/" + dirname + "/" + dirname + ".manifest") :
				log.info("Found " + filename + " to convert")
				log.info("Neutering Valve strings...")
				log.debug("****************************************")
				g = open("files/convert/" + filename, "rb")
				file = g.read( )
				origsize = len(file)
				g.close( )

				if config["public_ip"] != "0.0.0.0" :
					replace_strings = globalvars.replace_string(False)
					replace_strings_name = globalvars.replace_string_name(False) + globalvars.replace_string_name_space(False)
				else:
					replace_strings = globalvars.replace_string(True)
					replace_strings_name = globalvars.replace_string_name(True) + globalvars.replace_string_name_space(True)

				"""file = find_replace1(file,log, replace_strings)
				file = find_replace2(file,log,origsize, replace_strings_name)
				file = replace_ip_addresses(file, log, config)
				file = replace_ips_combined(file, log, config, origsize)"""
				file = parallel_process_file(file, log, config, origsize, replace_strings, replace_strings_name)

				with open("files/temp/" + dirname + ".neutered.gcf", "wb") as h:
					h.write(file)

				log.info("Converting fixed gcf to cache...")
				gcf2storage("files/temp/" + dirname + ".neutered.gcf")

				os.remove("files/temp/" + dirname + ".neutered.gcf")
				log.debug("****************************************")

def replace_loopback_ips(file, log, server_ip, event):
	if not config["server_ip"] == "127.0.0.1" :
		for ip in globalvars.loopback_ips:
			loc = file.find(ip)
			if loc != -1:
				replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
				file = file[:loc] + replace_ip + file[loc + 16:]
				log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")
				# Verify replacement
				verify_replacement(file, loc, replace_ip, log)
		event.set()

def find_replace1(file, log, replacement_tuple, event):
	for (search, replace, info) in replacement_tuple:
		missinglength = len(search) - len(replace)
		if missinglength < 0:
			log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
		else:
			padding = b'\x00' * max(0, missinglength)  # Add padding if necessary
			start = 0
			while True:
				loc = file.find(search, start)
				if loc == -1:
					break
				file = file[:loc] + replace + padding + file[loc + len(search):]
				log.debug(f"Replaced {info} at location {loc:08x} with {replace + padding}")
				# Verify replacement
				verify_replacement(file, loc, replace + padding, log)
				start = loc + len(replace) + len(padding)
	event.set()

def find_replace2(file, log, origsize, replacement_tuple, event):
	for search, replace, info in replacement_tuple:
		missinglength = len(search) - len(replace)
		if missinglength < 0:
			log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
			continue
		replace_extended = replace + (b'\x20' * missinglength) if missinglength > 0 else replace
		start = 0
		while True:
			loc = file.find(search, start)
			if loc == -1:
				break
			file = file[:loc] + replace_extended + file[loc + len(search):]
			log.debug(f"Replaced {info} at location {loc:08x} with {replace_extended}")
			# Verify replacement
			verify_replacement(file, loc, replace_extended, log)
			start = loc + len(replace_extended)
	event.set()


def replace_ips_combined(file, log, config, origsize, event):
	server_ip = config["public_ip"] if config["public_ip"] != "0.0.0.0" else config["server_ip"]
	server_ip_encoded = server_ip.encode()

	# Combine extraips and ip_addresses into a single list for iteration
	all_ips = globalvars.extraips + globalvars.ip_addresses

	for ip in all_ips:
		loc = file.find(ip)
		if loc != -1:
			replace_ip = server_ip_encoded + (b'\x00' * (16 - len(server_ip_encoded)))
			file = file[:loc] + replace_ip + file[loc + 16:]
			log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")
			# Verify replacement
			verify_replacement(file, loc, replace_ip, log)
	event.set()

def verify_replacement(file, location, expected, log):
	actual = file[location:location+len(expected)]
	if actual == expected:
		log.debug(f"Verification successful at location {location:08x}")
	else:
		log.debug(f"Verification failed at location {location:08x}. Expected {expected}, found {actual}")