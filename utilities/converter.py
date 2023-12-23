import binascii
import logging
import os
import struct
import concurrent.futures

import globalvars
from config import get_config as read_config
from gcf_to_storage import gcf2storage

config = read_config()
global_changes = {}


def replace_ip_addresses(file, log, config):
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
            global_changes[loc] = (len(search), replace)
            log.debug(message)
            log.debug(f"Replaced IP {ip} at location {loc:08x} with {replace}")

    # CC expiry date field replacement
    search = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
    replace = binascii.a2b_hex(b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
    loc = file.find(search)
    if loc != -1:
        global_changes[loc] = (len(search), replace)
        log.debug("Replaced CC expiry date field")
        log.debug(f"Replaced CC expiry date field at location {loc:08x} with {replace}")


def find_replace1(file, log, replacement_tuple):
    for (search, replace, info) in replacement_tuple:
        missinglength = len(search) - len(replace)
        if missinglength < 0:
            log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
        else:
            padding = b'\x00' * max(0, missinglength)
            start = 0
            while True:
                loc = file.find(search, start)
                if loc == -1:
                    break
                global_changes[loc] = (len(search), replace + padding)
                log.debug(f"Replaced {info} at location {loc:08x} with {replace + padding}")
                start = loc + len(replace) + len(padding)


def find_replace2(file, log, origsize, replacement_tuple):
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
            global_changes[loc] = (len(search), replace_extended)
            log.debug(f"Replaced {info} at location {loc:08x} with {replace_extended}")
            start = loc + len(replace_extended)


def replace_ips_combined(file, log, config, origsize):
    server_ip = config["public_ip"] if config["public_ip"] != "0.0.0.0" else config["server_ip"]
    server_ip_encoded = server_ip.encode()
    all_ips = globalvars.extraips + globalvars.ip_addresses
    for ip in all_ips:
        loc = file.find(ip)
        if loc != -1:
            replace_ip = server_ip_encoded + (b'\x00' * (16 - len(server_ip_encoded)))
            global_changes[loc] = (16, replace_ip)
            log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")


def replace_loopback_ips(file, log, server_ip):
    if not config["server_ip"] == "127.0.0.1":
        for ip in globalvars.loopback_ips:
            loc = file.find(ip)
            if loc != -1:
                replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
                global_changes[loc] = (16, replace_ip)
                log.debug(f"Replaced IP {ip.decode()} at location {loc:08x} with {replace_ip}")

def apply_changes(original_file):
    for loc, (length, replace) in sorted(global_changes.items()):
        original_file = original_file[:loc] + replace + original_file[loc+length:]
    return original_file


def parallel_process_file(file, log, config, origsize, replace_strings, replace_strings_name):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(find_replace1, file, log, replace_strings),
            executor.submit(find_replace2, file, log, origsize, replace_strings_name),
            executor.submit(replace_ip_addresses, file, log, config),
            executor.submit(replace_ips_combined, file, log, config, origsize),
            executor.submit(replace_loopback_ips, file, log, globalvars.server_ip_b)
        ]
        concurrent.futures.wait(futures)


def convertgcf():
    log = logging.getLogger("converters")
    for filename in os.listdir("files/convert/"):
        if filename.endswith(".gcf"):
            with open("files/convert/" + filename, "rb") as g:
                file = g.read()
                origsize = len(file)

                if config["public_ip"] != "0.0.0.0":
                    replace_strings = globalvars.replace_string(False)
                    replace_strings_name = globalvars.replace_string_name(False) + globalvars.replace_string_name_space(False)
                else:
                    replace_strings = globalvars.replace_string(True)
                    replace_strings_name = globalvars.replace_string_name(True) + globalvars.replace_string_name_space(True)

                parallel_process_file(file, log, config, origsize, replace_strings, replace_strings_name)

                modified_file = apply_changes(file)
                with open(f"files/temp/{filename}.neutered.gcf", "wb") as h:
                    h.write(modified_file)

                log.info("Converting fixed gcf to cache...")
                gcf2storage(f"files/temp/{filename}.neutered.gcf")