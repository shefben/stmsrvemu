import binascii
import logging
import pickle
import struct
import zlib

import ipcalc

import globalvars
import utilities
import utils
from utilities import encryption
from utilities.networkbuffer import NetworkBuffer
from utilities.networkhandler import TCPNetworkHandler

log = logging.getLogger("BETA1CS")


class Beta1_ContentServer(TCPNetworkHandler):

    def __init__(self, port, config):
        super().__init__(config, port)  # Create an instance of NetworkHandler

    def handle_client(self, client_socket, client_address):
        clientid = str(client_address) + ": "
        log.info(f"{clientid}Connected to Beta 1 Content Server")

        msg = client_socket.recv(4)
        version, = struct.unpack(">I", msg)
        if version != 0 or version != 1:
            log.warning(f"{clientid}Bad Content Server Protocol version: {version}")
            client_socket.send(b"\x00")
            client_socket.close()

        client_socket.send(b"\x01")
        storagesopen = 0
        storages = {}
        while True:
            if version == 0:
                msg = client_socket.recv_withlen_short()
            else:
                msg = client_socket.recv_withlen()

            if msg[0] == 0:
                (appid, verid) = struct.unpack(">II", msg[1:9])
                log.info(f"{clientid}User Requesting AppID: {str(appid)}  Version: {str(verid)}")

                key = b"\x69" * 0x10
                if encryption.validate_mac(msg[9:], key):
                    log.info(f"{clientid}MAC validated OK")

                data = NetworkBuffer(msg[9:])

                ticketsize, = struct.unpack(">H", data.extract_u16())
                ticket = data.extract_buffer(ticketsize)

                ptext = encryption.beta_decrypt_message_v1(data.extract_remaining()[:-20], key)

                log.info(clientid + "Opening application %d %d" % (appid, verid))

                try:
                    s = utilities.storages.Storage(appid, self.config["storagedir"], verid)
                except Exception:
                    log.error("Application not installed! %d %d" % (appid, verid))

                    # reply = struct.pack(">LLc", connid, messageid, b"\x01")
                    reply = struct.pack(">B", 0)
                    client_socket.send(reply)

                storageid = storagesopen
                storagesopen += 1

                storages[storageid] = s
                storages[storageid].app = appid
                storages[storageid].version = verid

                try:
                    with open(f"files/beta1_manifest/{str(appid)}_{str(verid)}.manifest", "rb") as g:
                        manifest = g.read()
                except Exception as e:
                    log.error(f"{clientid}Beta 1 (2002) Cannot Load Manifest for AppID: {appid} Version: {verid}")
                    log.error(e)
                    reply = struct.pack(">B", 0)
                    client_socket.send(reply)

                manifest_appid = struct.unpack('<L', manifest[4:8])[0]
                manifest_verid = struct.unpack('<L', manifest[8:12])[0]
                log.debug(clientid + ("Manifest ID: %s Version: %s" % (manifest_appid, manifest_verid)))

                if (int(manifest_appid) != int(appid)) or (int(manifest_verid) != int(verid)):
                    log.error("Manifest doesn't match requested file: (%s, %s) (%s, %s)" % (appid, verid, manifest_appid, manifest_verid))
                    reply = struct.pack(">B", 0)
                    client_socket.send(reply)
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

                # reply = b"\xff" + fingerprint[::-1]
                client_socket.send(b"\x66" + manifest[30:38] + b"\x01")  # send manifest fingerprint

                index_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".index"
                dat_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".dat"
                # Load the index
                with open(index_file, 'rb') as f:
                    index_data = pickle.load(f)
                try:
                    dat_file_handle.close()
                except:
                    pass

                dat_file_handle = open(dat_file, 'rb')

                while True:
                    data = client_socket.recv(1)

                    if len(data) == 0:  # User disconnected / connection was interrupted
                        client_socket.close()
                        break

                    if data[0] == 2:  # Send manifest
                        log.info(f"{clientid}Sending manifest")
                        client_socket.send(struct.pack(">I", len(manifest)) + manifest, False)
                    # TODO BEN, DO WE NEED PACKETS 3 AND 4? WHAT ABOUT UPDATE INFO??

                    elif msg[0] == 5:
                        data = client_socket.recv(12)

                        fileid, offset, length = struct.unpack(">III", msg)
                        index_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".index"
                        dat_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".dat"
                        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)):
                            filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "internal")
                        else:
                            filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle, "external")
                        client_socket.send(b"\x01" + struct.pack(">II", len(filedata), 0), False)
                        for i in range(0, len(filedata), 0x2000):
                            chunk = filedata[i:i + 0x2000]
                            client_socket.send(struct.pack(">I", len(chunk)) + chunk, False)
                    try:
                        dat_file_handle.close()
                    except:
                        pass
            else:
                log.warning(f"{binascii.b2a_hex(data[0:1])} - Invalid Command!")
                client_socket.send(b"\x01")

            break