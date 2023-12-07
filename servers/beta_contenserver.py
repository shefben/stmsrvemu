import logging
import struct

from utilities.networkbuffer import NetworkBuffer
from utilities import encryption
from utilities.networkhandler import TCPNetworkHandler

log = logging.getLogger("BETA1CS")


class Beta1ContentServer(TCPNetworkHandler):

    def __init__(self, port, config):
        super().__init__(config, port)  # Create an instance of NetworkHandler

    def handle_client(self, client_socket, client_address):
        clientid = str(client_address) + ": "
        log.info(clientid + "Connected to Client Update Server")

        msg = client_socket.recv(4)
        version, = struct.unpack(">I", msg)
        if version != 0  or version != 1:
            log.warning(f"{clientid} Bad contentserver version: {version}")
            client_socket.send(b"\x00")
            client_socket.close()

        client_socket.send(b"\x01")

        while True:
            msg = client_socket.recv_withlen_short()

            if msg[0] == 0:
                (appid, verid) = struct.unpack(">II", msg[1 :9])
                log.info(f"{clientid} User Requesting AppID: {str(appid)}  Version: {str(verid)}")

                key = b"\x69" * 0x10
                if encryption.validate_mac(msg[9 :], key) :
                    print("MAC validated OK")

                data = NetworkBuffer(msg[9:])

                ticketsize, = struct.unpack(">H", data.extract_u16())
                ticket = data.extract_buffer(ticketsize)

                ptext = encryption.beta_decrypt_message_v1(data.extract_remaining()[:-20], key)

                try :
                    with open(f"files/beta1_manifest/{str(appid)}_{str(verid)}.manifest", "rb") as g :
                        manifest = g.read( )
                except Exception as e :
                    log.error(f"Beta 1 (2002) Cannot Load Manifest for AppID: {appid} Version: {verid}")
                    log.error(e)

                client_socket.send(b"\x66" + manifest[30:38] + b"\x01") # send manifest fingerprint

                while True:
                    data = client_socket.recv(1)

                    if len(data) == 0 : # User disconnected / connection was interrupted
                        break

                    if data[0] == 2 : # Send manifest
                        client_socket.send(struct.pack(">I", len(manifest)) + manifest)

                    elif msg[0] == 5:
                        data = client_socket.recv(12)

                        fileid, offset, length = struct.unpack(">III", msg)
                        index_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".index"
                        dat_file = self.config["betastoragedir"] + str(appid) + "_" + str(verid) + ".dat"
                        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) :
                            filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle,
                                                           "internal")
                        else :
                            filedata = utils.readfile_beta(fileid, offset, length, index_data, dat_file_handle,
                                                           "external")


            else :
                raise Exception("unknown subcommand")

            break