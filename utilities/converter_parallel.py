import binascii
import logging
import os
import struct
import gc
#import concurrent.futures
import threading

import globalvars
from config import get_config as read_config
from gcf_to_storage import gcf2storage

config = read_config()
log = logging.getLogger("converters")


def replace_ip_addresses(file, server_ip):
	changes = {}
	dirsrv_port = config["dir_server_port"].encode('latin-1')
	ip_replacements = [
		(b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038", dirsrv_port, "Replaced directory server IP group 1"),
		(b"207.173.177.11:27030 207.173.177.12:27030", dirsrv_port, "Replaced directory server IP group 5"),
		(b"hlmaster1.hlauth.net:27010", 				b"27010", 	"Replaced default HL Master server DNS"),
		(b"207.173.177.11:27010", 						b"27010", 	"Replaced default HL Master server IP 1"),
		(b"207.173.177.12:27010", 						b"27010", 	"Replaced default HL Master server IP 2"),
		(b"207.173.177.11:27011", 						b"27011", 	"Replaced default HL2 Master server IP 1"),
		(b"207.173.177.12:27011", 						b"27011", 	"Replaced default HL2 Master server IP 2"),
		(b"tracker.valvesoftware.com:1200", 			b"1200",  	"Replaced Tracker Chat server DNS"),
		(b'"207.173.177.42:1200"',						b"1200", 	"Replaced Tracker Chat server 1"),
		(b'"207.173.177.43:1200"', 						b"1200", 	"Replaced Tracker Chat server 2"),
		(b'"207.173.177.44:1200"', 						b"1200", 	"Replaced Tracker Chat server 3"),
		(b'"207.173.177.45:1200"', 						b"1200", 	"Replaced Tracker Chat server 4")
	]

	for search, port, message in ip_replacements:
		ip = server_ip + b":" + port
		search_length = len(search)
		ip_length = len(ip)
		num_to_replace = search_length // ip_length
		ips = (ip + b" ") * num_to_replace
		replace = ips + (b'\x00' * (search_length - len(ips)))
		loc = file.find(search)
		if loc != -1:
			changes[loc] = (len(search), replace)
			#log.debug(message)
			#log.debug(f"Replaced IP {ip} at location {loc:08x} with {replace}")
	return changes


def cc_replacement(file):
	changes = {}
	search = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
	replace = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
	loc = file.find(search)
	#print(loc)
	if loc != -1:
		#print("cc replaced")
		changes[loc] = (len(search), replace)
		#changes[loc] = (len(search), replace)
		#log.debug(f"Replaced CC expiry date field at location {loc:08x} with {replace}")
	return changes


def find_replace1(file, replacement_tuple):
	changes = {}
	for (search, replace, info) in replacement_tuple:
		missinglength = len(search) - len(replace)
		if missinglength < 0:
			continue
			#log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
		else:
			padding = b'\x00' * max(0, missinglength)
			start = 0
			while True:
				loc = file.find(search, start)
				if loc == -1:
					break
				changes[loc] = (len(search), replace + padding)
				#log.debug(f"Replaced {info} at location {loc:08x} with {replace + padding}")
				start = loc + len(replace) + len(padding)
	return changes

def find_replace2(file, replacement_tuple, is_space_padding):
	changes = {}
	for (search, replace, info) in replacement_tuple:
		missinglength = len(search) - len(replace)
		if missinglength < 0:
			continue
			#log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
		elif missinglength ==0 :
			start = 0
			while True:
				loc = file.find(search, start)
				if loc == -1:
					break
				changes[loc] = (len(search), replace)
				#log.debug(f"Replaced {info} at location {loc:08x} with {replace + padding}")
				start = loc + len(replace)
		else:
			padding = b'\x20' * missinglength if is_space_padding else b'\x00' * missinglength
			start = 0
			while True:
				loc = file.find(search, start)
				if loc == -1:
					break

				changes[loc] = (len(search), replace + padding)
				#log.debug(f"Replaced {info} at location {loc:08x} with {replace + padding}")
				start = loc + len(replace) + len(padding)
	return changes

def replace_ips_combined(file, server_ip):
	changes = {}
	all_ips = globalvars.extraips + globalvars.ip_addresses
	for ip in all_ips:
		loc = file.find(ip)
		if loc != -1:
			replace_ip = server_ip + (b'\x00' * (16 - len(server_ip)))
			changes[loc] = (16, replace_ip)
			#log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")
	return changes


def replace_loopback_ips(file, server_ip):
	changes = {}
	if not config["server_ip"] == "127.0.0.1":
		for ip in globalvars.loopback_ips:
			loc = file.find(ip)
			if loc != -1:
				replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
				changes[loc] = (16, replace_ip)
				#log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")
	return changes


def apply_changes(original_file, changes):
	for loc, (length, replace) in sorted(changes.items()):
		original_file = original_file[:loc] + replace + original_file[loc + length:]
	return original_file


"""def parallel_process_file(file, server_ip, replace_strings, replace_strings_name):

	with concurrent.futures.ThreadPoolExecutor() as executor:
		futures = [
			executor.submit(find_replace1, file, replace_strings),
			executor.submit(find_replace2, file, replace_strings_name),
			executor.submit(replace_ip_addresses, file, server_ip),
			executor.submit(replace_ips_combined, file, server_ip),
			executor.submit(replace_loopback_ips, file, server_ip),
			executor.submit(cc_replacement, file)
		]

		combined_changes = {}
		for future in concurrent.futures.as_completed(futures):
			changes = future.result()
			combined_changes.update(changes)

	return apply_changes(file, combined_changes)"""


def parallel_process_file(file, server_ip, replace_strings, replace_strings_name, replace_strings_name_space):
	# Create separate functions to run in threads
	functions = [
		lambda: find_replace1(file, replace_strings),
		lambda: find_replace2(file, replace_strings_name_space, True),
		lambda: find_replace2(file, replace_strings_name, False),
		lambda: replace_ip_addresses(file, server_ip),
		lambda: replace_ips_combined(file, server_ip),
		lambda: replace_loopback_ips(file, server_ip),
		lambda: cc_replacement(file)
	]

	results = [None] * len(functions)
	threads = []

	def thread_function(index, func):
		results[index] = func()

	# Start threads
	for i, func in enumerate(functions):
		thread = threading.Thread(target=thread_function, args=(i, func))
		threads.append(thread)
		thread.start()

	# Wait for all threads to complete
	for thread in threads:
		thread.join()

	combined_changes = {}
	for changes in results:
		combined_changes.update(changes)

	return apply_changes(file, combined_changes)


def convertgcf():
	islan = False if config["public_ip"] != "0.0.0.0" else True
	server_ip = config["public_ip"] if config["public_ip"] != "0.0.0.0" else config["server_ip"]
	server_ip = server_ip.encode('latin-1')

	for filename in os.listdir("files/convert/"):
		if filename.endswith(".gcf"):
			with open("files/convert/" + filename, "rb") as g:
				file = g.read()

				depotid = struct.unpack("<L", file[12:16])[0]
				versionid = struct.unpack("<L", file[16:20])[0]
				dirname = str(depotid) + "_" + str(versionid)
				if not os.path.isfile("files/cache/" + dirname + "/" + dirname + ".manifest") :
					modified_file = parallel_process_file(file, server_ip, globalvars.replace_string(islan), globalvars.replace_string_name_space(islan), globalvars.replace_string_name(islan))

					with open(f"files/temp/{filename}.neutered.gcf", "wb") as h:
						h.write(modified_file)

					log.info("Converting fixed gcf to cache...")
					gcf2storage(f"files/temp/{filename}.neutered.gcf")
					os.remove("files/temp/" + filename + ".neutered.gcf")
					log.debug("****************************************")
					# Explicitly delete the file variable and call garbage collection
					del file
					gc.collect()