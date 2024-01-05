import binascii
import logging
import os
import struct

import globalvars
from config import read_config
from gcf_to_storage import gcf2storage
from globalvars import dedicated_server_appids, game_engine_file_appids

config = read_config()
log = logging.getLogger("converter")


def convertgcf():
    server_ip_wan = config["public_ip"].encode('latin-1')
    server_ip_lan = config["server_ip"].encode('latin-1')
    dirsrv_port = config["dir_server_port"].encode('latin-1')
    if config["public_ip"] == "0.0.0.0":
        islan = True
    else:
        islan = False

    for filename in os.listdir("files/convert/"):
        if filename.endswith(".gcf"):
            with open(os.path.join("files", "convert", filename), "rb") as g:
                h = g.read(20)

            depotid = struct.unpack("<L", h[12:16])[0]
            versionid = struct.unpack("<L", h[16:20])[0]
            dirname = f"{depotid}_{versionid}"
            files_to_check = [f"{dirname}.manifest"]

            if any(not os.path.isfile(os.path.join("files", "cache", dirname, filename)) for filename in files_to_check):
                log.info(f"Found {filename} to convert")
                log.info("Neutering Valve strings...")
                log.debug("****************************************")

                with open(os.path.join("files", "convert", filename), "rb") as g:
                    file_content = g.read()
                if not islan and depotid in dedicated_server_appids or depotid in game_engine_file_appids:
                    # Process for WAN
                    processed_file_wan = process_file(file_content, server_ip_wan, dirsrv_port, filename, False)
                    output_filename_wan = os.path.join("files", "temp", f"{dirname}_wan.neutered.gcf")
                    write_processed_file(processed_file_wan, output_filename_wan)

                    # Process for LAN
                    processed_file_lan = process_file(file_content, server_ip_lan, dirsrv_port, filename, True)
                    output_filename_lan = os.path.join("files", "temp", f"{dirname}_lan.neutered.gcf")
                    write_processed_file(processed_file_lan, output_filename_lan)
                else:
                    server_ip = server_ip_lan if islan else server_ip_wan
                    processed_file_lan = process_file(file_content, server_ip, dirsrv_port, filename, islan)
                    output_filename_lan = os.path.join("files", "temp", f"{dirname}.neutered.gcf")
                    write_processed_file(processed_file_lan, output_filename_lan)

                log.debug("****************************************")


def process_file(file_content, server_ip, dirsrv_port, filename, islan):
    searchip = [(b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038", server_ip + b":" + dirsrv_port + b" " + server_ip + b":" + dirsrv_port + b" ", "Replaced directory server IP group 1"), (b"207.173.177.11:27030 207.173.177.12:27030", server_ip + b":" + dirsrv_port + b" ", "Replaced directory server IP group 5"), (b"hlmaster1.hlauth.net:27010", server_ip + b":27010", "Replaced default HL Master server DNS"), (b"207.173.177.11:27010", server_ip + b":27010", "Replaced default HL Master server IP 1"), (b"207.173.177.12:27010", server_ip + b":27010", "Replaced default HL Master server IP 2"), (b"207.173.177.11:27011", server_ip + b":27011", "Replaced default HL2 Master server IP 1"), (b"207.173.177.12:27011", server_ip + b":27011", "Replaced default HL2 Master server IP 2"), (b"tracker.valvesoftware.com:1200", server_ip + b":1200", "Replaced Tracker Chat server DNS"),
            (b'"207.173.177.42:1200"', b'"' + server_ip + b':1200"', "Replaced Tracker Chat server 1"), (b'"207.173.177.43:1200"', b'"' + server_ip + b':1200"', "Replaced Tracker Chat server 2"), (b'"207.173.177.44:1200"', b'"' + server_ip + b':1200"', "Replaced Tracker Chat server 3"), (b'"207.173.177.45:1200"', b'"' + server_ip + b':1200"', "Replaced Tracker Chat server 4")]

    for search, replace, message in searchip:
        search_length = len(search)
        replace_padded = replace.ljust(search_length, b'\x00')
        if search in file_content:
            file_content = file_content.replace(search, replace_padded)
            log.debug(message)

    for ip in globalvars.extraips + globalvars.ip_addresses:
        file_content = ip_replacer(file_content, filename, ip, server_ip)

    if server_ip != b"127.0.0.1":
        for ip in globalvars.loopback_ips:
            file_content = ip_replacer(file_content, filename, ip, server_ip)

    for (search, replace, info) in globalvars.replace_string(islan):
        file_content = find_replace(file_content, info, replace, search, False)

    if config["http_port"] != "steam":
        for (search, replace, info) in globalvars.replace_string_name_space(islan):
            file_content = find_replace(file_content, info, replace, search, True)

        for (search, replace, info) in globalvars.replace_string_name(islan):
            file_content = find_replace(file_content, info, replace, search, False)

    expiration_search = binascii.a2b_hex("2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
    expiration_replace = binascii.a2b_hex("2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
    file_content = file_content.replace(expiration_search, expiration_replace)
    log.debug("Replaced CC expiry date field")

    return file_content


def write_processed_file(file_content, output_filename):
    with open(output_filename, "wb") as h:
        h.write(file_content)
    log.info(f"Converting fixed gcf to cache...")
    gcf2storage(output_filename)
    os.remove(output_filename)


def ip_replacer(file, filename, ip, server_ip):
    loc = file.find(ip)
    if loc != -1:
        replace_ip = server_ip.ljust(16, b"\x00")
        file = file[:loc] + replace_ip + file[loc + 16:]
        log.debug(f"{filename}: Found and replaced IP {ip} at location {loc:08x}")
    return file


def find_replace(file, info, replace, search, null_padded = False):
    search_length = len(search)
    replace_length = len(replace)

    # Early exit if replace is longer than search
    if replace_length > search_length:
        log.debug(f"WARNING: Cannot replace {info} {search} with {replace} as it's too long")
        return file

    # Perform the replacement directly if lengths are equal
    if replace_length == search_length:
        file = file.replace(search, replace)
    else:
        # Decide the padding character based on the 'null_padded' flag
        padding_char = b'\x20' if null_padded else b'\x00'
        # Pad the replace string and perform the replacement
        padded_replace = replace.ljust(search_length, padding_char)
        file = file.replace(search, padded_replace)
        log.debug(f"Replaced {info} {search} with {padded_replace}")

    return file