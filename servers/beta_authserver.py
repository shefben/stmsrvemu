import ast
import binascii
import hashlib
import hmac
import logging
import pprint
import socket as pysocket
import struct
import time

import ipcalc
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15

import globalvars
import utils
from utilities import blobs, encryption
from utilities.database import beta1_authdb
from utilities.database.dbengine import create_database_driver
from utilities.networkbuffer import NetworkBuffer
from utilities.networkhandler import TCPNetworkHandler

log = logging.getLogger("BetaAuthSRV")

icon_files = {
    b"\x00\x00\x00\x00" : "hl.ico",
    b"\x01\x00\x00\x00" : "cs.ico",
    b"\x02\x00\x00\x00" : "dmc.ico",
    b"\x03\x00\x00\x00" : "tfc.ico",
    b"\x04\x00\x00\x00" : "dod.ico",
    b"\x05\x00\x00\x00" : "tracker.ico"
}

def k(n) :
    return struct.pack("<I", n)


def determine_recv_func(version, clientid, client_socket) :
    if version == 0 :
        return client_socket.recv_withlen_short
    elif version == 1 :
        return client_socket.recv_withlen
    else :
        log.warning(f"{clientid}  User tried to Login to beta auth with unknown steam version: {version}")
        client_socket.close( )
        return None


class Beta1AuthServer(TCPNetworkHandler) :

    def __init__(self, port, config) :
        # do not send to dir server, dir is not used for beta 1 steam
        # server_type = "Betaserver"
        # Create an instance of NetworkHandler
        super().__init__(config, port)

        self.db_session = create_database_driver(config['database_type'])
        self.db_conn = beta1_authdb.Beta1AuthDatabase(self.db_session)
        self.CDR = self.initialize_CDR()


    def initialize_CDR(self) :
        try:
            with open("files/beta1_blobs/secondblob.py", "r") as g :
                CDR_py = g.read( )
                CDR = ast.literal_eval(CDR_py[7 :len(CDR_py)])
        except Exception as e:
            log.error("Beta 1 (2002) Auth Server Cannot Load SecondBlob.py!!")
            log.error(e)
        try :
            for app_id, icon_file in icon_files.items( ) :
                with open(f"files/beta1_icons/{icon_file}", "rb") as g :
                    CDR[b"\x01\x00\x00\x00"][app_id][b"\x06\x00\x00\x00"] = struct.pack("<I", 128)  # MinCacheFileSizeMB (size 4)
                    CDR[b"\x01\x00\x00\x00"][app_id][b"\x07\x00\x00\x00"] = struct.pack("<I", 256)  # MaxCacheFileSizeMB
                    CDR[b"\x01\x00\x00\x00"][app_id][b"\x09\x00\x00\x00"][b"\x01\x00\x00\x00"] = g.read( )   # AppIconsRecord (subblob)
            # initialize the subscriptions x03 entry
            for i in range(16, 21) :  # 16 is 0x10, 21 is 0x15 (one after 0x14)
                subid = struct.pack(">I", i)
                CDR[b"\x02\x00\x00\x00"][subid][b"\x03\x00\x00\x00"] = struct.pack("<Q", 1000 * 1000 * 60 * 60 * 24 * 4 * 7)

            CDR[b"\x03\x00\x00\x00"] = bytes.fromhex("e0e0e0e0e0e0e000") # LastChangedExistingAppOrSubscriptionTime

        except FileNotFoundError :
            log.error(f"{icon_file} file not found")
        except Exception as e :
            log.error("Beta 1 (2002) Auth Server Cannot Load Game Icons!!")
            log.error(e)

        return CDR


    def handle_client(self, client_socket, client_address) :
        clientid = str(client_address) + ": "
        log.info(f"{clientid} Connected to Beta Auth Server")

        data = client_socket.recv(1)
        family = data[0]

        if family != 1 :
            log.info(f"{clientid} Unknown Family ID")
            return

        message = client_socket.recv_all(4)
        version, = struct.unpack(">I", message)
        message = client_socket.recv_all(4)
        client_internal_ip = message[: :-1]
        client_external_ip = pysocket.inet_aton(self.address[0])

        client_socket.send(b"\x01" + client_external_ip[: :-1])

        recv_func = determine_recv_func(version, clientid, client_socket)
        if recv_func is None :
            return

        subcommand = data[0]
        subcommand_actions = {
            0  : lambda : self.get_ccr(client_socket, clientid, message, version),
            1  : lambda : self.create_user(client_socket, recv_func),
            2  : lambda : self.login(client_external_ip, client_internal_ip, client_socket, clientid, data, version),
            11 : lambda : self.get_cdr(client_socket, clientid)
        }
        client_ip_tuple = (client_address, client_external_ip, client_internal_ip)
        content_ticket_subcommands = (3, 4, 5, 6, 9, 10)
        if subcommand in content_ticket_subcommands :
            self.handle_content_ticket_login(subcommand, client_socket, client_ip_tuple, clientid, message, data)
        elif subcommand in subcommand_actions :
            subcommand_actions[subcommand]( )
        else :
            log.info(f"{clientid} Unknown Sub Command ID")

    def handle_content_ticket_login(self, subcommand, client_socket, client_ip_tuple, clientid, message, data) :
        (client_address, client_external_ip, client_internal_ip) = client_ip_tuple
        log.info(f"{clientid} Attempting Content Ticket Login")

        innerkey = bytes.fromhex("10231230211281239191238542314233")

        if not encryption.validate_mac(message[1 :], innerkey) :
            log.info(f"{clientid} MAC validated ERROR")
            return

        network_buffer = NetworkBuffer(data[1 :])

        ticketsize, = struct.unpack(">H", network_buffer.extract_u16( ))
        ticket = network_buffer.extract_buffer(ticketsize)

        decryptedmessage = encryption.decrypt_message(network_buffer.extract_remaining( )[:-20], innerkey)
        decryptedmessage = NetworkBuffer(decryptedmessage)

        username_len1 = struct.unpack("<H", decryptedmessage.extract_u16( ))
        username1 = decryptedmessage.extract_buffer(username_len1)

        username_len2 = struct.unpack("<H", decryptedmessage.extract_u16( ))
        username2 = decryptedmessage.extract_buffer(username_len2)

        if len(username1) != username_len1 or len(username2) != username_len2 or username1 != username2 :
            log.info(f"{clientid} Bad Username!")
            client_socket.send(b"\x02")
            return

        log.info(f"{clientid} Using Username: {username1}")

        controlhash = hashlib.sha1(client_external_ip + client_internal_ip).digest( )
        client_time = utils.steamtime_to_unixtime(
            encryption.binaryxor(decryptedmessage.extract_buffer(8), controlhash[:8]))
        # skew = int(time.time( ) - client_time)

        subcommand_functions = {
            3  : lambda : self.delete_user(client_socket, clientid),  # Placeholder function
            4  : lambda : self.logout(client_socket, clientid),
            5  : lambda : self.modify_subscription(client_socket, clientid, network_buffer, subcommand, username1),
            6  : lambda : self.modify_subscription(client_socket, clientid, network_buffer, subcommand, username1),
            9  : lambda : self.refresh_login(client_socket, clientid, decryptedmessage, username1),
            10 : lambda : self.get_contentticket(client_address, client_socket, innerkey)
        }

        if subcommand in subcommand_functions :
            subcommand_functions[subcommand]( )
        else :
            log.info(f"{clientid} Unknown Content Ticket Sub Command ID")

    def get_cdr(self, client_socket, clientid) :
        log.info(f"{clientid} Requested CDR")
        binblob = blobs.blob_serialize(self.CDR)
        binblob = struct.pack(">I", len(binblob)) + binblob
        client_socket.send(binblob)

    def get_contentticket(self, client_address, client_socket, innerkey) :
        currtime = time.time( )
        client_ticket = b"\x69" * 0x10  # key used for MAC signature
        client_ticket += utils.unixtime_to_steamtime(currtime)  # TicketCreationTime
        client_ticket += utils.unixtime_to_steamtime(currtime + 86400)  # TicketValidUntilTime
        if str(client_address[0]) in ipcalc.Network(str(globalvars.server_net)) :
            client_ticket += utils.encodeIP(
                    (self.config["server_ip"], self.config["beta_content_server_port"]))
        else :
            client_ticket += utils.encodeIP(
                    (self.config["public_ip"], self.config["beta_content_server_port"]))
        server_ticket = b"\x55" * 0x80  # ticket must be between 100 and 1000 bytes
        ticket = b"\x00\x00" + encryption.beta_encrypt_message(client_ticket, innerkey)
        ticket += struct.pack(">H", len(server_ticket)) + server_ticket
        ticket_signed = ticket + hmac.digest(client_ticket[0 :16], ticket, hashlib.sha1)
        # for feb2002 the ticket size is encoded as u16
        client_socket.send(b"\x00\x01" + struct.pack(">H", len(ticket_signed)) + ticket_signed)

    def refresh_login(self, client_socket, clientid, decryptedmessage, username1) :
        log.info(clientid + "[Refresh Login] User Refreshing Login")
        decryptedmessage.finish_extracting( )
        user_registry = self.db_conn.get_user_blob(username1, self.CDR)
        userreg_blob = blobs.blob_serialize(user_registry)
        client_socket.send(struct.pack(">I", len(userreg_blob)) + userreg_blob)

    def modify_subscription(self, client_socket, clientid, network_buffer, subcommand, username1) :
        subid_bin = network_buffer.extract_remaining( )
        if len(subid_bin) != 4 :
            log.error(f"{clientid} tried using a bad subscription packet")
        subid, = struct.unpack("<I", subid_bin)
        if subid_bin not in self.CDR[k(2)] :
            log.error(f"{clientid} User requested Invalid Subscription id: {subid}")
        subscription_action = 1 if subcommand == 6 else 0
        self.db_conn.edit_subscription(username1, subid, remove_sub=subscription_action)
        userblob = self.db_conn.get_user_blob(username1, self.CDR)
        binblob = blobs.blob_serialize(userblob)
        client_socket.send(struct.pack(">I", len(binblob)) + binblob)
        if subcommand == 6 :
            log.info(f"{clientid} [UnSubscribe] User is UnSubscribing to Subscription ID: {subid}")
        else :
            log.info(f"{clientid} [Subscribe] User Subscribing to Subscription ID: {subid}")

    def login(self, client_external_ip, client_internal_ip, client_socket, clientid, data, version) :
        log.info(f"{clientid} Attempting Login")
        network_buffer = NetworkBuffer(data[1 :])
        username_len1 = struct.unpack(">H", network_buffer.extract_u16( ))
        username1 = network_buffer.extract_buffer(username_len1)
        username_len2 = struct.unpack(">H", network_buffer.extract_u16( ))
        username2 = network_buffer.extract_buffer(username_len2)
        remaining = network_buffer.extract_remaining( )
        if len(username1) != username_len1 or len(username2) != username_len2 or username1 != username2 or len(
                remaining) != 0 :
            log.info(f"{clientid} Bad Username!")
        log.info(f"{clientid} Using Username: ", username1)
        salteddigest, personalsalt = self.db_conn.get_salt_hash(username1)
        if salteddigest is None :
            # TODO proper error to client
            log.error(f"{clientid} Error reading user '{username1}' salted digest!!")
            self.client_socket.drop( )
        key = salteddigest[0 :16]
        client_socket.send(binascii.a2b_hex(personalsalt))
        if version == 0 :
            encryptedmessage = client_socket.recv_withlen_short( )

        elif version == 1 :
            encryptedmessage = client_socket.recv_withlen( )
        decryptedmessage = encryption.decrypt_message(encryptedmessage, key)
        if len(decryptedmessage) != 12 :
            log.info(f"{clientid} bad plaintext size")
        if decryptedmessage[8 :12] != client_internal_ip :
            log.info(f"{clientid} internal IP doesn't match (bad decryption?)")
        controlhash = hashlib.sha1(client_external_ip + client_internal_ip).digest( )
        client_time = utils.steamtime_to_unixtime(encryption.binaryxor(decryptedmessage[0 :8], controlhash[0 :8]))
        skew = int(time.time( ) - client_time)
        if abs(skew) >= 3600 :
            log.info(f"{clientid} skew too large (bad decryption?)")
        blob = blobs.blob_serialize(self.db_conn.get_user_blob(username1, self.CDR))
        # just sending a plaintext blob for now
        blob_encrypted = struct.pack(">I", len(blob)) + blob
        currtime = int(time.time( ))
        innerkey = bytes.fromhex("10231230211281239191238542314233")
        times = utils.unixtime_to_steamtime(currtime) + utils.unixtime_to_steamtime(
                currtime + (60 * 60 * 24 * 28))
        subheader = innerkey + times
        subheader_encrypted = b"\x00\x00" + encryption.beta_encrypt_message(subheader, key)
        unknown_part = b"\x00\x80" + (b"\xff" * 0x80)
        ticket = subheader_encrypted + unknown_part + blob_encrypted
        ticket_signed = ticket + hmac.digest(innerkey, ticket, hashlib.sha1)
        tgt_command = b"\x01"  # AuthenticateAndRequestTGT command
        steamtime = utils.unixtime_to_steamtime(time.time( ))
        ticket_full = tgt_command + steamtime + b"\x00\xd2\x49\x6b\x00\x00\x00\x00" + struct.pack(">I",
                                                                                                  len(ticket_signed)) + ticket_signed
        client_socket.send(ticket_full)
        return remaining

    def get_ccr(self, client_socket, clientid, message, version) :
        log.info(f"{clientid} Recieved CCR Request")
        # product version, file version embedded in executable
        if version == 0 :
            client_socket.send(struct.pack("<IIIIIIII", 0, 6, 0, 0, 1, 0, 0, 0))
        elif version == 1 :
            client_socket.send(struct.pack("<IIIIIIII", 0, 6, 1, 0, 1, 1, 0, 0))
        message = client_socket.recv(1)
        log.info(clientid + "Sent \'ccr\' to client")
        return message

    def delete_user(self, client_socket, clientid):
        log.info(f"{clientid} User Attempted to delete account, Operation Not supported")


    def logout(self, client_socket, clientid):
        log.info(f"{clientid} User logged off")
        client_socket.close()
    def create_user(self, client_socket, recv_func) :
        data = bytes.fromhex("30819d300d06092a864886f70d010101050003818b0030818702818100") + self.config[
                                                                                                 "net_key_n"][
                                                                                             2 :] + bytes.fromhex(
                "020111")
        client_socket.send_withlen_short(data)
        client_socket.send_withlen_short(pkcs1_15.new(encryption.network_key).sign(SHA1.new(data)))
        data = recv_func( )
        cl_data = NetworkBuffer(data)
        seskey_size = struct.unpack(">H", cl_data.extract_u16())
        enc_seskey = cl_data.extract_buffer(seskey_size)
        sessionkey = PKCS1_OAEP.new(encryption.network_key).decrypt(enc_seskey)
        print(f"session key {repr(sessionkey)}")
        if encryption.validate_mac(cl_data, sessionkey) :
            print("validated OK")
        ctext_size = cl_data.extract_u32( )
        ctext = cl_data.extract_buffer(ctext_size)
        print("ctext", repr(ctext))
        ptext = encryption.beta_decrypt_message_v1(ctext[10 :], sessionkey)
        print("ptext", repr(ptext))
        unser_blob = blobs.blob_unserialize(ptext)
        pprint.pprint(unser_blob)
        # Add user to database
        adduser = self.db_conn.create_user(unser_blob)
        if adduser :
            client_socket.send(b"\x01")  # User Added
        else :
            client_socket.send(b"\x00")  # Error adding user!
        return data