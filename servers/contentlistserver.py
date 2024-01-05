import binascii
import logging
import socket as pysocket
import struct
import threading
import time

import ipcalc

import globalvars
import utils
from listmanagers.contentlistmanager import manager
from listmanagers.contentserverlist_utilities import receive_removal, unpack_contentserver_info
from utilities import encryption
from utilities.networkhandler import TCPNetworkHandler

csdsConnectionCount = 0

log = logging.getLogger("CSDServer")


def expired_servers_thread():
    while True:
        time.sleep(3600)  # 1 hour
        manager.remove_old_entries()


class contentlistserver(TCPNetworkHandler):

    def __init__(self, port, config):
        self.server_type = "CSDServer"
        super(contentlistserver, self).__init__(config, int(port), self.server_type)  # Create an instance of NetworkHandler

        thread = threading.Thread(target = expired_servers_thread)  # Thread for removing servers older than 1 hour
        thread.daemon = True
        thread.start()

        # TODO Ben note: Figure out how to get the appid's and versions from the sdk contentserver.  # ideas include: if a packet exists for getting the app list, have csds send the packet and parse the response  # or put sdk contentserver in a folder within stmserver that we can parse through the files ourselves

        # if globalvars.use_sdk == "true" :  #      sdk_server_info = {  #     'ip_address': str(self.config["sdk_ip"]),  #     'port': int(self.config["sdk_port"]),  #     'region': globalvars.cs_region,  #     'timestamp': 1623276000  # }

    def handle_client(self, client_socket, client_address):
        global csdsConnectionCount

        reply = b""
        # TODO BEN NOTE: Add peering to this server!

        clientid = str(client_address) + ": "
        log.info(f"{clientid} Connected to Content List Server ")

        # Determine if connection is local or external
        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
            islan = True
        else:
            islan = False

    msg = client_socket.recv(4)
    if msg == b"\x00\x4f\x8c\x11":
        self.acceptcontentservers(log, clientid, client_socket)
    elif msg == b"\x00\x00\x00\x02":
        csdsConnectionCount += 1

        client_socket.send(b"\x01")

        msg = client_socket.recv_withlen()

        if msg[0:1] == b"\x03":  # send out file servers (Which have the initial packages)
            reply = self.packet_getpkgcs_x03(clientid, islan)

else:
if msg[2:3] == b"\x00":
    reply = self.packet_getpkgcs(clientid, islan)

elif msg[2:3] == b"\x01":
    reply = self.packet_getcswithapps(clientid, msg)
else:
    log.warning(f"Invalid message! {binascii.b2a_hex(msg).decode()}")

client_socket.send_withlen(reply)
client_socket.close()
log.info(f"{clientid} Disconnected from Content Server Directory Server")


def packet_getpkgcs(self, clientid, islan):


    log.info(f"{clientid} Sending out Content Servers with packages (0x00)")
all_results, all_count = manager.get_empty_or_no_applist_entries(islan)

if all_count > 0:
    reply = struct.pack(">H", 1) + b"\x00\x00\x00\x00"
    for ip, port in all_results:
        print(f"pkg update servers: {ip} {port}")
        bin_ip = utils.encodeIP((ip, port))
        reply += (bin_ip + bin_ip)
else:
    reply = b"\x00\x00"

return reply


def packet_getcswithapps(self, clientid, msg):
    (appnum, version, numservers, region) = struct.unpack(">xxxLLHLxxxxxxxx", msg)
    log.info(f"{clientid} send which server has content for app {appnum} {version} {numservers} {region}")
    results, count = manager.find_ip_address(str(region), str(appnum), str(version))

    if count > 0:
        reply = struct.pack(">H", count) + b"\x00\x00\x00\x00"
        for ip, port in results:
            ip_port_tuple = (ip, port)
            bin_ip = utils.encodeIP(ip_port_tuple)
            reply += bin_ip + bin_ip
    else:
        reply = struct.pack(">H", 0)  # Default reply value if no matching server is found

    if self.config["sdk_ip"] != "0.0.0.0":
        log.info(f"{clientid} Handing off to SDK server for app {appnum} {version}")
        ip_port_tuple = (self.config["sdk_ip"], self.config["sdk_port"])
        bin_ip = utils.encodeIP(ip_port_tuple)
        reply = struct.pack(">H", 1) + b"\x00\x00\x00\x00" + bin_ip + bin_ip

    return reply

    def packet_getpkgcs_x03(self, clientid, islan):

        log.info(f"{clientid} Sending out Content Servers with packages (0x03)")
    all_results, all_count = manager.get_empty_or_no_applist_entries(islan)


if all_count > 0:
    reply = struct.pack(">H", 1) + b"\x00\x00\x00\x00"  # is this needed?? BEN NOTE
    for ip, port in all_results:
        ip_port_tuple = (ip, port)
        reply += utils.encodeIP(ip_port_tuple)
        # reply += struct.pack(">H",all_count) + utils.encodeIP(ip_port_tuple)
        break
    return reply


def acceptcontentservers(self, log, clientid, client_socket):  # Used for registering content servers with csds
    client_socket.send(b"\x01")  # handshake confirmed
    length_packet = client_socket.recv(4)
    unpacked_length = struct.unpack('!I', length_packet[:4])[0]

    client_socket.send(b"\x01")
    msg = client_socket.recv(unpacked_length)
    command = msg[0]

    log.debug(binascii.b2a_hex(command).decode())

    if command == b"\x2b":  # Add single server entry to the list

        wan_ip, lan_ip, port, region, received_applist = unpack_contentserver_info(msg)
        try:
            wan_ip = pysocket.inet_aton(wan_ip.encode('latin-1'))
            lan_ip = pysocket.inet_aton(lan_ip.encode('latin-1'))
        except pysocket.error:
            log.warning(f"{clientid} Failed to decrypt CS Heartbeat packet: {binascii.b2a_hex(msg).decode()}")
            client_socket.send(b"\x00")  # message decryption failed, the only response we give for failure
            client_socket.close()
            log.info(f"{clientid} Disconnected from Content Server Directory Server")
            return

        if manager.add_contentserver_info(wan_ip, lan_ip, int(port), region, received_applist):
            client_socket.send(b"\x01")
            log.info(f"[{region}] {clientid} Added to Content Server Directory Server")
        else:
            client_socket.send(b"\x00")
            log.error(f"[{region}] {clientid} Failed to register with Content Server Directory Server")

    elif command == b"\x2e":  # Remove server entry from the list

        packed_data = msg[1:]
        decrypted_msg = encryption.decrypt(packed_data, globalvars.peer_password)
        wan_ip, lan_ip, port, region = receive_removal(decrypted_msg)
        try:
            wan_ip = pysocket.inet_aton(wan_ip)
            lan_ip = pysocket.inet_aton(lan_ip)
        except pysocket.error:
            log.warning(f"{clientid} Failed to decrypt CS Removal packet: {binascii.b2a_hex(msg).decode()}")
            client_socket.send(b"\x00")  # message decryption failed, the only response we give for failure
            client_socket.close()
            log.info(f"{clientid} Disconnected from Content Server Directory Server")
            return

        if manager.remove_entry(wan_ip, lan_ip, port, region) is True:
            client_socket.send(b"\x01")
            log.info(f"[{region}] {clientid} Removed server from Content Server Directory Server")
        else:  # couldnt remove server because: doesnt exists or problem with list
            client_socket.send(b"\x01")
            log.info(f"[{region}] {clientid} There was an issue removing the server from Content Server Directory Server")