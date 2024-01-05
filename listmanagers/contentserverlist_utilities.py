import logging
import socket
import struct
import time
from builtins import str

import globalvars
from globalvars import config
from utilities import encryption

log = logging.getLogger("CSLSTMGR")


def receive_removal(packed_info):
    unpacked_info = struct.unpack('!16s I 16s', packed_info)
    ip_address = unpacked_info[0][:-1]
    port = unpacked_info[1]
    region = unpacked_info[2][:-1]
    return ip_address, port, region


def send_removal(port, region):
    if globalvars.public_ip == "0.0.0.0":
        server_ip = globalvars.server_ip
    else:
        server_ip = globalvars.public_ip
    reg = region

    packed_info = struct.pack('!16s I 16s', server_ip, port, reg)

    return remove_from_dir("\x2e" + encryption.encrypt(packed_info, globalvars.peer_password))


def send_heartbeat(contentserver_info, applist, ispkg = False):
    packed_info = ""
    packed_info += contentserver_info['wan_ip'] + b'\x00'
    print(f"public IP: {contentserver_info['wan_ip']}")
    packed_info += contentserver_info['lan_ip'] + b'\x00'
    print(f"LAN IP: {contentserver_info['lan_ip']}")
    packed_info += struct.pack('H', contentserver_info['port'])
    packed_info += contentserver_info['region'] + '\x00'
    packed_info += str(contentserver_info['timestamp']) + '\x00'
    if ispkg is False:
        packed_info += applist

    return heartbeat("\x2b" + encryption.encrypt(packed_info, globalvars.peer_password))


def unpack_contentserver_info(encrypted_data):
    decrypted_data = encryption.decrypt(encrypted_data[1:], globalvars.peer_password)

    wan_ip = ""
    ip_index = 0
    while decrypted_data[ip_index] != '\x00':
        wan_ip += decrypted_data[ip_index]
        ip_index += 1
    ip_index += 1

    lan_ip = ""
    ip_index = 0
    while decrypted_data[ip_index] != '\x00':
        lan_ip += decrypted_data[ip_index]
        ip_index += 1
    ip_index += 1

    port = struct.unpack('H', decrypted_data[ip_index:ip_index + 2])[0]
    ip_index += 2

    region = ""
    while decrypted_data[ip_index] != '\x00':
        region += decrypted_data[ip_index]
        ip_index += 1
    ip_index += 1

    timestamp = ""
    while decrypted_data[ip_index] != '\x00':
        timestamp += decrypted_data[ip_index]
        ip_index += 1
    timestamp = float(timestamp)
    ip_index += 1

    applist_data = decrypted_data[ip_index:]
    applist = []

    if len(applist_data) > 0:
        app_index = 0
        while app_index < len(applist_data):
            appid = ""
            version = ""
            while app_index < len(applist_data) and applist_data[app_index] != '\x00':
                appid += applist_data[app_index]
                app_index += 1
            app_index += 1

            while app_index < len(applist_data) and applist_data[app_index:app_index + 2] != '\x00\x00':
                version += applist_data[app_index]
                app_index += 1
            app_index += 2

            applist.append([appid, version])
    else:
        return wan_ip, lan_ip, port, region, []
    return wan_ip, lan_ip, port, region, applist


def heartbeat(encrypted_buffer):
    if globalvars.public_ip == "0.0.0.0":
        csds_ipport = (globalvars.server_ip_b, config['contentdir_server_port'])
    else:
        csds_ipport = config["csds_ipport"]

    csds_ip, csds_port = csds_ipport.split(":")

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((str(csds_ip), int(csds_port)))  # Connect the socket to master dir server
            break  # Exit the loop if connection succeeds
        except socket.error as e:
            print(f"Connection error: {str(e)}")
            print("Retrying in 5 minutes...")
            time.sleep(5 * 60)  # Wait for 5 minutes before retrying

    data = b"\x00\x4f\x8c\x11"
    sock.send(data)  # Send the 'im a dir server packet' packet

    handshake = sock.recv(1)  # wait for a reply

    if handshake == b'\x01':
        packed_length = struct.pack('!I', len(encrypted_buffer))  # Assuming the length fits into
        # an unsigned integer (4 bytes)

        sock.send(packed_length)
        response = sock.recv(1)
        if response == b'\x01':
            sock.send(encrypted_buffer)
            confirmation = sock.recv(1)
            if confirmation != b'\x01':
                log.warning("Content Server failed to register server to Content Server Directory Server ")
    else:
        log.warning("Content Server failed to contact Content Server Directory Server ")

    sock.close()


def remove_from_dir(encrypted_buffer):
    csds_ipport = config["csds_ipport"]
    csds_ip, csds_port = csds_ipport.split(":")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((csds_ip, csds_port))  # Connect the socket to master dir server

    data = b"\x00\x4f\x8c\x11"
    sock.send(data)  # Send the 'im a dir server packet' packet

    handshake = sock.recv(1)  # wait for a reply

    if handshake == b'\x01':
        sock.send(encrypted_buffer)
        confirmation = sock.recv(1)  # wait for a reply
        if confirmation != b'\x01':
            log.warning("Content Server failed to register server to Content Server Directory Server ")
    else:
        log.warning("Content Server failed to contact Content Server Directory Server ")

    sock.close()