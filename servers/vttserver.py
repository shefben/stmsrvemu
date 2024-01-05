import binascii
import logging
import struct

import utilities.encryption
from utilities.networkhandler import TCPNetworkHandler


class vttserver(TCPNetworkHandler):
    def __init__(self, port, config):
        super(vttserver, self).__init__(config, int(port), "")

    def handle_client(self, client_socket, client_address):
        log = logging.getLogger("vttsrv")
        clientid = str(client_address) + ": "

        log.info(f"{clientid} Connected to VTT Server")

        error_count = 0

        while True:
            try:

                # config_update = read_config()

                command = client_socket.recv(26)

                log.debug("COMMAND :" + binascii.b2a_hex(command).decode() + ":")

                if command[0:8] == b"\x53\x45\x4e\x44\x4d\x41\x43\x20":  # SENDMAC (v2) + MAC in caps and hyphens
                    # print("SENDMAC")
                    log.info(f"{clientid} SENDMAC received")
                    macaddress = binascii.unhexlify(binascii.b2a_hex(command))[9:26]
                    log.info(f"{clientid} MAC address received: {str(macaddress)}")
                    # TO DO: create MAC filter here

                    if self.config["cafe_use_mac_auth"].lower() == "true":
                        mac_count = 0
                        cafemacs = (self.config["cafemacs"].split(";"))
                        # print(len(cafemacs))
                        while mac_count < len(cafemacs):
                            # print(cafemacs[mac_count])
                            if macaddress == cafemacs[mac_count]:
                                client_socket.send(b"\x01\x00\x00\x00")  # VALID
                                break
                            mac_count += 1
                            if mac_count == len(cafemacs):
                                client_socket.send(b"\xfd\xff\xff\xff")  # NO VALID MAC
                                break
                    else:
                        client_socket.send(b"\x01\x00\x00\x00")  # ALWAYS VALID

                elif command[0:6] == b"\x53\x45\x54\x4d\x41\x43":  # SETMAC (v1)
                    log.info(f"{clientid} SETMAC received")
                    client_socket.send(b"\x01\x00\x00\x00")

                elif command[0:4] == b"\x00\x00\xff\xff":  # Response (v1)
                    log.info(f"{clientid} RESPONSE sent")
                    client_socket.send(b"\x01\x00\x00\x00")  # INCORRECT AND UNKNOWN FOR 1.4

                elif command[0:9] == b"\x43\x48\x41\x4c\x4c\x45\x4e\x47\x45":  # CHALLENGE (v1)
                    log.info(f"{clientid} CHALLENGE received")
                    client_socket.send(b"\xff\xff\x00\x00")  # CHALLENGE reply (can be anything, is the inverse of the client reply)

                elif command[5:12] == b"\x47\x45\x54\x49\x4e\x46\x4f":  # GETINFO
                    # print(binascii.b2a_hex(command))
                    log.info(f"{clientid} GETINFO received")
                    cafeuser = self.config["cafeuser"]
                    cafepass = self.config["cafepass"]
                    username_dec = cafeuser + "%" + cafepass
                    username_enc = utilities.encryption.textxor(username_dec)
                    # print(username_dec)
                    # print(username_enc)
                    reply = struct.pack("<L", len(username_enc)) + username_enc
                    # print(binascii.b2a_hex(reply))
                    client_socket.send(reply)

                elif command[0:8] == b"\x53\x45\x4e\x44\x4d\x49\x4e\x53" or command[5:13] == b"\x53\x45\x4e\x44\x4d\x49\x4e\x53":  # SENDMINS
                    log.info(f"{clientid} SENDMINS received")
                    # client_socket.send(b"\x01\x00\x00\x00") #FAKE MINS
                    reply = struct.pack("<L", int(self.config["cafetime"]))
                    client_socket.send(reply)

                elif command[0:8] == b"\x47\x45\x54\x49\x4e\x46\x4f\x20":  # GETINFO AGAIN
                    # print(binascii.b2a_hex(command))
                    log.info(f"{clientid} GETINFO received")
                    cafeuser = self.config["cafeuser"]
                    cafepass = self.config["cafepass"]
                    username_dec = cafeuser + "%" + cafepass
                    username_enc = utilities.encryption.textxor(username_dec)
                    # print(username_dec)
                    # print(username_enc)
                    reply = struct.pack("<L", len(username_enc)) + username_enc
                    # print(binascii.b2a_hex(reply))
                    client_socket.send(reply)

                elif command[0:8] == b"\x50\x49\x4e\x47\x20\x20\x20\x20":  # PING
                    log.info(f"{clientid} PING received")

                elif len(command) == 5:
                    log.warning(f"{clientid} Client failed to log in")

                elif len(command) == 0:
                    log.info(f"{clientid} Client ended session")
                    break

                else:
                    if error_count == 1:
                        log.info(f"{clientid} UNKNOWN VTT COMMAND {binascii.b2a_hex(command[0:26]).decode()}")
                    error_count += 1
                    if error_count > 5:
                        # log.info(f"{clientid} CAS client logged off or errored, disconnecting socket")
                        break

            except:
                log.error(f"{clientid} An error occured between the client and the VTT")
                break

        client_socket.close()
        log.info(f"{clientid} Disconnected from VTT Server")