import threading
import logging
import struct
import binascii
import time
import ipaddress
import os.path
import ast
import zlib
import socket as pysocket
import config
import utilities
import blob_utilities
import encryption
import emu_socket
import steamemu.logger
import globalvars
import auth_utilities
#from database import MySQLDatabase, SQLiteDatabase
#from mysql_class import MySQLConnector
from Crypto.Hash import SHA
from networkhandler import TCPNetworkHandler

log = logging.getLogger("AuthenticationSRV")


class authserver(TCPNetworkHandler):
 #   mysqlconn = 0

    def __init__(self, port, config):
        server_type = "authserver"
        # Create an instance of NetworkHandler
        super(authserver, self).__init__(config, port, server_type)
        #self.mysqlconn = MySQLDatabase('localhost', 'root', '', 'stmserver')
        #self.mysqlconn.connect()
        # mysqlconn = MySQLConnector() # Initialize mysql connection
        # mysqlconn.connect() # Connect Persistently

    def handle_client(self, clientsocket, address):
        server_string = utilities.convert_ip_port(str(self.config['validation_ip']), int(self.config['validation_port']))
        final_srvstring = server_string + server_string
        servers = binascii.b2a_hex("7F0000019A697F0000019A69")
        # region
        # need to figure out a way to assign steamid's.  hopefully with mysql
        #steamid = binascii.a2b_hex("0000" + "80808000" + "00000000")

        clientid = str(address) + ": "
		# BEN NOTE: Change to SQL!
        if os.path.isfile("files/firstblob.py") :
            f = open("files/firstblob.py", "r")
            firstblob = f.read()
            f.close()
            execdict = {}
            execfile("files/firstblob.py", execdict)
            blob = blob_utilities.blob_serialize(execdict["blob"])
            steamui_hex = blob['\x02\x00\x00\x00']
            steamui_ver = struct.unpack('<I', steamui_hex)[0]
        else :
            f = open("files/firstblob.bin", "rb")
            blob = f.read()
            f.close()
            firstblob_bin = blob
            if firstblob_bin[0:2] == "\x01\x43":
                firstblob_bin = zlib.decompress(firstblob_bin[20:])
            firstblob_unser = blob_utilities.blob_unserialize(firstblob_bin)
            firstblob = blob_utilities.blob_dump(firstblob_unser)

            firstblob_list = firstblob.split("\n")
            steamui_hex = firstblob_list[3][25:41]
            steamui_ver = int(steamui_hex[14:16] + steamui_hex[10:12] + steamui_hex[6:8] + steamui_hex[2:4], 16)

        if steamui_ver < 61 :  # guessing steamui version when steam client interface v2 changed to v3
            globalvars.tgt_version = "1"
            log.debug(clientid + "TGT version set to 1")
        else :
            globalvars.tgt_version = "2"  # config file states 2 as default
            log.debug(clientid + "TGT version set to 2")

        log.info(clientid + "Connected to Auth Server")

        command = clientsocket.recv(13)

        log.debug(":" + binascii.b2a_hex(command[1:5]) + ":")
        log.debug(":" + binascii.b2a_hex(command) + ":")
# region
        if command[1:5] == "\x00\x00\x00\x04" or command[1:5] == "\x00\x00\x00\x01" or command[1:5] == "\x00\x00\x00\x02" or command[1:5] == "\x00\x00\x00\x03" :

            clientsocket.send( "\x00" + pysocket.inet_aton(clientsocket.address[0]))
            log.debug((str(pysocket.inet_aton(clientsocket.address[0]))))
            log.debug((str(pysocket.inet_ntoa(pysocket.inet_aton(clientsocket.address[0])))))

            command = clientsocket.recv_withlen()

            if len(command) > 1 and len(command) < 256 :

                usernamelen = struct.unpack(">H", command[1:3])[0]

                userblob = {}

                username = command[3:3 + usernamelen]

                if username == "" :
                    username = "2003"
                log.info(clientid + "Processing logon for user: " + username)  # 7465737431
                log.debug(clientid + "Username length: " + str(usernamelen))  # 0005
                # username length and username is then received again

                
                # First check if the user exists, then check if the user is banned
                if (os.path.isfile("files/users/" + username + ".py")) :#and legacyuser == 0 :
                    with open("files/users/" + username + ".py", 'r') as f:
                        userblobstr = f.read()
                        userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                    blocked = binascii.b2a_hex(userblob['\x0c\x00\x00\x00'])
                    if blocked == "0001" :
                        log.info(clientid + "Blocked user: " + username)
                        clientsocket.send("\x00\x00\x00\x00\x00\x00\x00\x00")
                        command = clientsocket.recv_withlen()
                        steamtime = utilities.unixtime_to_steamtime(time.time())
                        tgt_command = "\x04"  # BLOCKED
                        padding = "\x00" * 1222
                        ticket_full = tgt_command + steamtime + padding
                        clientsocket.send(ticket_full)
                    else :
                        # password hash generated by client on user creation, passwordCypherRijndaelKey/authenticationRijndaelKey in TINserver
                        #key, personalsalt = mysqlconn.get_userpass_stuff(username)
                        personalsalt = userblob['\x05\x00\x00\x00'][username]['\x02\x00\x00\x00']
                        # print(personalsalt)
                        clientsocket.send(personalsalt)  # NEW SALT PER USER
                        command = clientsocket.recv_withlen()
                        key = userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00'][0:16] #password hash generated by client on user creation, passwordCypherRijndaelKey/authenticationRijndaelKey in TINserver

                        # print(binascii.b2a_hex(key))
                        IV = command[0:16]
                        # print(binascii.b2a_hex(IV))
                        encrypted = command[20:36]
                        # print(binascii.b2a_hex(encrypted))
                        decodedmessage = binascii.b2a_hex(encryption.aes_decrypt(key, IV, encrypted))
                        log.debug(clientid + "Authentication package: " + decodedmessage)

                        if not decodedmessage.endswith("04040404") :
                            wrongpass = "1"
                            log.info(clientid + "Incorrect password entered for: " + username)
                        else :
                            wrongpass = "0"

                        # create login ticket
                        execdict = {}
                        execdict_new = {}
						
						# BEN NOTE: Change to SQL!
                        with open("files/users/" + username + ".py", 'r') as f :
                            userblobstr = f.read()
                            execdict = ast.literal_eval(userblobstr[16:len(userblobstr)])
							
                        secretkey = {'\x05\x00\x00\x00'}

                        def without_keys(d, keys) :
                            return {x: d[x] for x in d if x not in keys}
                        execdict_new = without_keys(execdict, secretkey)
                        # print(execdict)
                        # print(execdict_new)
                        blob = blob_utilities.blob_serialize(execdict_new)
                        # print(blob)
                        bloblen = len(blob)
                        log.debug("Blob length: " + str(bloblen))
                        # ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        innerkey = binascii.a2b_hex("10231230211281239191238542314233")
                        # ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        innerIV = binascii.a2b_hex("12899c8312213a123321321321543344")
                        blob_encrypted = encryption.aes_encrypt(innerkey, innerIV, blob)
                        blob_encrypted = struct.pack("<L", bloblen) + innerIV + blob_encrypted
                        blob_signature = encryption.sign_message(innerkey, blob_encrypted)
                        blob_encrypted_len = 10 + len(blob_encrypted) + 20
                        blob_encrypted = struct.pack(">L", blob_encrypted_len) + "\x01\x45" + struct.pack("<LL", blob_encrypted_len, 0) + blob_encrypted + blob_signature
                        currtime = time.time()
                        outerIV = binascii.a2b_hex("92183129534234231231312123123353")
                        #steamid = binascii.a2b_hex("0000" + "80808000" + "00000000")
                        steamUniverse = "0000"
                        steamid = binascii.a2b_hex(steamUniverse + binascii.b2a_hex(userblob['\x06\x00\x00\x00'][username]['\x01\x00\x00\x00'][0:16]))
                        #servers = binascii.a2b_hex("451ca0939a69451ca0949a69")
                        #authport = struct.pack("<L", int(port))
						
                        if self.config["public_ip"] != "0.0.0.0" :
                            bin_ip = utilities.encodeIP((self.config["public_ip"], self.config["validation_port"]))
                        else :
                            bin_ip = utilities.encodeIP((self.config["server_ip"], self.config["validation_port"]))
							
                        #bin_ip = steam.encodeIP(("172.21.0.20", "27039"))
                        servers = bin_ip + bin_ip
                        times = utilities.unixtime_to_steamtime(currtime) + utilities.unixtime_to_steamtime(currtime + (60*60*24*28))
                        subheader = innerkey + steamid + servers + times
                        subheader_encrypted = encryption.aes_encrypt(key, outerIV, subheader)
                        subhead_decr_len = "\x00\x36"
                        subhead_encr_len = "\x00\x40"
						
                        if globalvars.tgt_version == "1" :  # nullData1
                            subheader_encrypted = "\x00\x01" + outerIV + subhead_decr_len + subhead_encr_len + subheader_encrypted  # TTicket_SubHeader (EncrData)
                            log.debug(clientid + "TGT Version: 1")  # v2 Steam
                        elif globalvars.tgt_version == "2" :
                            subheader_encrypted = "\x00\x02" + outerIV + subhead_decr_len + subhead_encr_len + subheader_encrypted
                            log.debug(clientid + "TGT Version: 2")  # v3 Steam
                        else :
                            subheader_encrypted = "\x00\x02" + outerIV + subhead_decr_len + subhead_encr_len + subheader_encrypted
                            # Assume v3 Steam
                            log.debug(clientid + "TGT Version: 2")
							
                        # unknown_part = "\x01\x68" + ("\xff" * 0x168) #THE ACTUAL TICKET!!!
                        # 0 = eVersionNum
                        # 1=eUniqueAccountName
                        # 2=eAccountUserName
                        # 3=eSteamInstanceID
                        # 4=eSteamLocalUserID
                        # 5=eClientExternalIPAddr
                        # 6=eClientLocalIPAddr
                        # 7=eUserIDTicketValidationServerIPAddr1
                        # 8=eUserIDTicketValidationServerport1
                        # 9=eUserIDTicketValidationServerIPAddr2
                        # 10=eUserIDTicketValidationServerport2
                        # 11=eClientToServerAESSessionKey
                        # 12=eTicketCreationTime
                        # 13=TicketValidUntilTime
                        # 14=ServerReadablePart
                        clientIP = pysocket.inet_aton(clientsocket.address[0])
                        publicIP = clientIP[::-1]
                        #subcommand3 = "\x00\x00\x00\x00"
                        data1_len_str = "\x00\x80"
                        # empty1 = ("\x00" * 0x80) #TTicketHeader unknown encrypted
                        data1 = username + username + "\x00\x01" + publicIP + clientIP + servers + key + times
                        data1_len_empty = int( 0x80 * 2) - len(binascii.b2a_hex(data1))
                        data1_full = data1 + ("\x00" * (data1_len_empty / 2))
                        # unknown encrypted - RSA sig?
                        empty3 = ("\x00" * 0x80)
                        username_len = len(username)
                        #username_len_packed = struct.pack(">H", 50 + username_len)
                        # SteamID
                        accountId = userblob['\x06\x00\x00\x00'][username]['\x01\x00\x00\x00'][0:16]
                        data2 = struct.pack(">L", len(username))
						
                        if globalvars.tgt_version == "1":
                            subcommand1 = "\x00\x01"  # for TGT v1
                            subcommand2 = ""  # missing for TGT v1
                            empty2_dec_len = "\x00\x42"
                            empty2_enc_len = "\x00\x50"
                            # empty2 = ("\x00" * 0x50) #160 chars long (80 int bytes) unknown encrypted
                            data2_len_empty = int(0x50 * 2) - len(binascii.b2a_hex(data2))
                            data2_full = data2 + ("\x00" * (data2_len_empty / 2))
                        elif globalvars.tgt_version == "2":
                            subcommand1 = "\x00\x02"  # for TGT v2
                            subcommand2 = "\x00\x10"  # steamID+clientIPaddress TGT v2 only
                            subcommand2 = subcommand2 + accountId + clientIP
                            empty2_dec_len = "\x00\x52"
                            empty2_enc_len = "\x00\x60"
                            # empty2 = ("\x00" * 0x60) #192 chars long (96 int bytes) unknown encrypted
                            data2_len_empty = int(0x60 * 2) - len(binascii.b2a_hex(data2))
                            data2_full = data2 + ("\x00" * (data2_len_empty / 2))
                        else:
                            subcommand1 = "\x00\x02"  # assume TGT v2
                            subcommand2 = "\x00\x10"  # steamID+clientIPaddress TGT v2 only
                            subcommand2 = subcommand2 + accountId + clientIP
                            empty2_dec_len = "\x00\x52"
                            empty2_enc_len = "\x00\x60"
                            # empty2 = ("\x00" * 0x60) # 192 chars long (96 int bytes) unknown encrypted
                            data2_len_empty = int(0x60 * 2) - len(binascii.b2a_hex(data2))
                            data2_full = data2 + ("\x00" * (data2_len_empty / 2))

                        #empty2 = username + empty2_empty[(len(username)):]
                        real_ticket = subcommand1 + data1_len_str + data1_full + IV + empty2_dec_len + empty2_enc_len + data2_full + subcommand2 + empty3
                        real_ticket_len = struct.pack(">H", len(real_ticket))  # TicketLen
                        #ticket = subheader_encrypted + unknown_part + blob_encrypted
                        ticket = subheader_encrypted + real_ticket_len + real_ticket + blob_encrypted

                        ticket_signed = ticket + encryption.sign_message(innerkey, ticket)

                        # tgt_command = "\x03" #Clock-skew too far out
                        if wrongpass == "1":
                            tgt_command = "\x02"  # Incorrect password
                        else:
                            tgt_command = "\x00"  # Authenticated # AuthenticateAndRequestTGT command

                        steamtime = utilities.unixtime_to_steamtime(time.time())
                        clock_skew_tolerance = "\x00\xd2\x49\x6b\x00\x00\x00\x00"
                        authenticate = tgt_command + steamtime + clock_skew_tolerance
                        writeAccountInformation = struct.pack(">L", len(ticket_signed)) + ticket_signed  # FULL TICKET (steamticket.bin)
                        clientsocket.send(authenticate + writeAccountInformation)

                else:
                    log.info(clientid + "Unknown user: " + username)
                    clientsocket.send("\x00\x00\x00\x00\x00\x00\x00\x00")
                    steamtime = utilities.unixtime_to_steamtime(time.time())
                    tgt_command = "\x01"  # UNKNOWN USER
                    padding = "\x00" * 1222
                    ticket_full = tgt_command + steamtime + padding
                    clientsocket.send(ticket_full)

            else :
                commandcode = command[0]
                if commandcode == "\x01" :  # Create User
                    log.info(clientid + "command: Create user")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
						binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)

                    reply = clientsocket.recv_withlen()

                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]

                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    # print(plaintext)
                    plainblob = blob_utilities.blob_unserialize(plaintext)
                    # print(plainblob)

                    username = plainblob['\x01\x00\x00\x00']
                    username_str = username.rstrip('\x00')

                    if auth_utilities.check_username(username_str, clientsocket) == 2 :
                        log.info(clientid + "Client Username Had Illegal Characters")
                        clientsocket.send('\x02')
                        clientsocket.close()
                    elif auth_utilities.check_username_exists(username_str) == 1 :
                        log.info(clientid + "Client's choosen username already exists'")
                        clientsocket.send('\x01')
                        clientsocket.close()
                    elif auth_utilities.check_email(email_str, clientsocket) == 3 :
                        log.info(clientid + "Client Email Had Illegal Characters")
                        clientsocket.send('\x03')
                        clientsocket.close()

                    #invalid6 = {'\x06\x00\x00\x00'}
                    #def without_keys(d, keys) :
                    #    return {x: d[x] for x in d if x not in keys}
                    
                    #plainblob_fixed = without_keys(plainblob, invalid6)
                    
                    #dict6 = {}
                    #dict6 = {'\x06\x00\x00\x00': {username_str: {'\x01\x00\x00\x00': '\x10\x20\x30\x40\x00\x00\x00\x00', '\x02\x00\x00\x00': '\x00\x01', '\x03\x00\x00\x00': {}}}}
                    
                    #plainblob_fixed.update(dict6)


                    newsteamid = os.urandom(4) + "\x00\x00\x00\x00" #generate random steamId
                    plainblob['\x06\x00\x00\x00'][username_str]['\x01\x00\x00\x00'] = newsteamid
                    
                    invalid7 = {'\x07\x00\x00\x00'}
                    def without_keys(d, keys) :
                        return {x: d[x] for x in d if x not in keys}
                    
                    plainblob_fixed = without_keys(plainblob, invalid7)
                    
                    dict7 = {}
                    dict7 = {'\x07\x00\x00\x00': {'\x00\x00\x00\x00': {'\x01\x00\x00\x00': '\xe0\xe0\xe0\xe0\xe0\xe0\xe0\x00', '\x02\x00\x00\x00': '\x00\x00\x00\x00\x00\x00\x00\x00', '\x03\x00\x00\x00': '\x01\x00', '\x05\x00\x00\x00': '\x00', '\x06\x00\x00\x00': '\x1f\x00'}}}
                    
                    plainblob_fixed.update(dict7)
                    
                    dictf = {}
                    dictf = {'\x0f\x00\x00\x00': {'\x00\x00\x00\x00': {'\x01\x00\x00\x00': '\x07', '\x02\x00\x00\x00': {}}}}
                    
                    plainblob_fixed.update(dictf)
                        
                    with open("files/users/" + username_str + ".py", 'w') as userblobfile :
                        userblobfile.write("user_registry = ")
                        userblobfile.write(str(plainblob_fixed))
                    

                    clientsocket.send("\x00")
                elif commandcode == "\x03" : # Delete Account  BEN NOTE: Not Operational; Nothing gets sent back, just delete user py or user from db and close connection.
                    log.info(clientid + "User Sent Delete Account Command [Not Functional]")
                    clientsocket.close()
                elif commandcode == "\x04" : # User Logged off,  Does not expect response.
                    log.info(clientid + "User Logged Off")
                    clientsocket.close()         
                elif commandcode == "\x05" : # Subscribe
                    log.info(clientid + "Subscribe to package")
                    ticket_full = binascii.b2a_hex(command)
                    command = ticket_full[0:2]
                    ticket_len = ticket_full[2:6]
                    tgt_ver = ticket_full[6:10]
                    data1_len = ticket_full[10:14]
                    data1_len = int(data1_len, 16) * 2
                    userIV = binascii.a2b_hex(ticket_full[14 + data1_len:14 + data1_len + 32])
                    username_len = ticket_full[314:318]
                    username = binascii.a2b_hex(ticket_full[14:14 + (int(username_len, 16) * 2)])
                    ticket_len = int(ticket_len, 16) * 2
                    ticket = ticket_full[2:ticket_len + 2]
                    postticketdata = ticket_full[2 + ticket_len + 4:]
                    key = binascii.a2b_hex("10231230211281239191238542314233")
                    iv = binascii.a2b_hex(postticketdata[0:32])
                    encdata_len = int(postticketdata[36:40], 16) * 2
                    encdata = postticketdata[40:40 + encdata_len]
                    decodedmessage = binascii.b2a_hex(encryption.aes_decrypt(key, iv, binascii.a2b_hex(encdata)))
                    decodedmessage = binascii.a2b_hex(decodedmessage)
                    username_len_new = struct.unpack("<H", decodedmessage[0:2])
                    username_len_new = (2 + username_len_new[0]) * 2
                    header = username_len_new + 8
                    blob_len = struct.unpack("<H", decodedmessage[header + 2:header + 4])
                    blob_len = (blob_len[0])
                    blob = (decodedmessage[header:header + blob_len])
                    padding_byte = blob[-1:]
                    padding_int = struct.unpack(">B", padding_byte)
                    blobnew = blob_utilities.blob_unserialize(decodedmessage[header:header + blob_len])
                    # ------------------------------------------------------------------
                    if (os.path.isfile("files/users/" + username + ".py")) :
                        execdict = {}
                        execdict_new = {}
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            execdict = ast.literal_eval(userblobstr[16:len(userblobstr)])
                            
                        steamtime = steam.unixtime_to_steamtime(time.time())
                        new_sub = {blobnew["\x01\x00\x00\x00"]: {'\x01\x00\x00\x00': steamtime, '\x02\x00\x00\x00': '\x00\x00\x00\x00\x00\x00\x00\x00', '\x03\x00\x00\x00': '\x00\x00', '\x05\x00\x00\x00': '\x00', '\x06\x00\x00\x00': '\x1f\x00'}}
                        new_buy = {blobnew["\x01\x00\x00\x00"] : blobnew["\x02\x00\x00\x00"]}
                        receipt_dict = {}
                        receipt_dict_01 = {}
                        receipt_sub_dict = {}
                        subid = new_buy.keys()[0]
                        execdict["\x07\x00\x00\x00"].update(new_sub)
                        execdict["\x0f\x00\x00\x00"].update(new_buy)
                        #pprint.pprint(new_sub)
                        #pprint.pprint(new_buy)
                        #pprint.pprint(subid)
                        if new_buy[subid]['\x02\x00\x00\x00']['\x01\x00\x00\x00'] == "WONCDKey\x00" or new_buy[subid]['\x02\x00\x00\x00']['\x01\x00\x00\x00'] == "ValveCDKey\x00" :
                            receipt_sub_dict["\x01\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x01\x00\x00\x00"]
                            #receipt_sub_dict["\x02\x00\x00\x00"] = str(random.randint(11111111, 99999999)) + "\x00" #should be 8 digit hash of key, FIX ME
                            receipt_sub_dict["\x02\x00\x00\x00"] = new_buy[subid]['\x02\x00\x00\x00']['\x02\x00\x00\x00'] + "\x00" #saving key for now for verification
                            receipt_dict_01["\x01\x00\x00\x00"] = "\x06"
                            receipt_dict_01["\x02\x00\x00\x00"] = receipt_sub_dict
                            receipt_dict[subid] = receipt_dict_01
                        else:
                            receipt_sub_dict["\x01\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x01\x00\x00\x00"]
                            receipt_sub_dict["\x02\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x02\x00\x00\x00"][12:]
                            receipt_sub_dict["\x03\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x03\x00\x00\x00"]
                            receipt_sub_dict["\x07\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x07\x00\x00\x00"]
                            receipt_sub_dict["\x08\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x08\x00\x00\x00"]
                            receipt_sub_dict["\x09\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x09\x00\x00\x00"]
                            receipt_sub_dict["\x0a\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x0a\x00\x00\x00"]
                            receipt_sub_dict["\x0b\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x0b\x00\x00\x00"]
                            receipt_sub_dict["\x0c\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x0c\x00\x00\x00"]
                            receipt_sub_dict["\x0d\x00\x00\x00"] = str(random.randint(111111, 999999)) + "\x00"
                            receipt_sub_dict["\x0e\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x14\x00\x00\x00"]
                            receipt_sub_dict["\x0f\x00\x00\x00"] = new_buy[subid]["\x02\x00\x00\x00"]["\x15\x00\x00\x00"]
                            receipt_sub_dict["\x10\x00\x00\x00"] = datetime.datetime.now().strftime("%d/%m/%Y") + "\x00"
                            receipt_sub_dict["\x11\x00\x00\x00"] = datetime.datetime.now().strftime("%H:%M:%S") + "\x00"
                            receipt_sub_dict["\x12\x00\x00\x00"] = str(random.randint(11111111, 99999999)) + "\x00"
                            receipt_sub_dict["\x13\x00\x00\x00"] = "\x00\x00\x00\x00"
                            receipt_dict_01["\x01\x00\x00\x00"] = "\x05"
                            receipt_dict_01["\x02\x00\x00\x00"] = receipt_sub_dict
                            receipt_dict[subid] = receipt_dict_01
                        new_buy.clear()
                        execdict["\x0f\x00\x00\x00"].update(receipt_dict)                        #BEN NOTE: Change to SQL!

                        with open("files/users/" + username + ".py", 'w') as g:
                            g.write("user_registry = " + str(execdict))
                        secretkey = {'\x05\x00\x00\x00'}

                        def without_keys(d, keys):
                            return {x: d[x] for x in d if x not in keys}
                        execdict_new = without_keys(execdict, secretkey)
                        # print(execdict)
                        # print(execdict_new)
                        blob = blob_utilities.blob_serialize(execdict_new)
                        # print(blob)
                        bloblen = len(blob)
                        log.debug("Blob length: " + str(bloblen))
                        innerkey = binascii.a2b_hex("10231230211281239191238542314233") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        #innerIV  = binascii.a2b_hex("12899c8312213a123321321321543344") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        innerIV  = binascii.a2b_hex("12899c8312213a123321321321543344") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        blob_encrypted = encryption.aes_encrypt(innerkey, innerIV, blob)
                        blob_encrypted = struct.pack("<L", bloblen) + innerIV + blob_encrypted
                        blob_signature = encryption.sign_message(innerkey, blob_encrypted)
                        blob_encrypted_len = 10 + len(blob_encrypted) + 20
                        blob_encrypted = struct.pack(">L", blob_encrypted_len) + "\x01\x45" + struct.pack("<LL", blob_encrypted_len, 0) + blob_encrypted + blob_signature
                        clientsocket.send("\x00" + blob_encrypted)
                elif commandcode == "\x06" : # Unsubscribe   BEN NOTE: Not Operational
                    log.info(clientid + "Unsubscribe [Not Functional]")
                    clientsocket.send("\x02")                       
                elif commandcode == "\x09" : # Ticket Login
                    ticket_full = binascii.b2a_hex(command)
                    command = ticket_full[0:2]
                    ticket_len = ticket_full[2:6]
                    tgt_ver = ticket_full[6:10]
                    data1_len = ticket_full[10:14]
                    data1_len = int(data1_len, 16) * 2
                    userIV = binascii.a2b_hex(ticket_full[14 + data1_len:14 + data1_len + 32])
                    username_len = ticket_full[314:318]
                    username = binascii.a2b_hex(ticket_full[14:14 + (int(username_len, 16) * 2)])
                    log.info(clientid + "Ticket login for: " + username)
                    ticket_len = int(ticket_len, 16) * 2
                    postticketdata = ticket_full[2 + ticket_len + 4:]
                    key = binascii.a2b_hex("10231230211281239191238542314233")
                    iv = binascii.a2b_hex(postticketdata[0:32])
                    encdata_len = int(postticketdata[36:40], 16) * 2
                    encdata = postticketdata[40:40 + encdata_len]
                    decodedmessage = binascii.b2a_hex(encryption.aes_decrypt(key, iv, binascii.a2b_hex(encdata)))
                    #------------------------------------------------------------------
					# BEN NOTE: Change to SQL
                    if (os.path.isfile("files/users/" + username + ".py")) :
                        #self.socket.send("\x00")
                        # create login ticket
                        execdict = {}
                        execdict_new = {}
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            execdict = ast.literal_eval(userblobstr[16:len(userblobstr)])
                        for sub_dict in execdict:
                            if sub_dict == "\x07\x00\x00\x00":
                                for sub_sub_dict in execdict[sub_dict]:
                                    if execdict[sub_dict][sub_sub_dict]["\x03\x00\x00\x00"] == "\x00\x00":
                                        execdict[sub_dict][sub_sub_dict]["\x03\x00\x00\x00"] = "\x01\x00"
                                        execdict[sub_dict][sub_sub_dict]["\x05\x00\x00\x00"] = "\x01"
                                        execdict[sub_dict][sub_sub_dict]["\x06\x00\x00\x00"] = "\x00\x00"
                        with open("files/users/" + username + ".py", 'w') as g:
                            g.write("user_registry = " + str(execdict))
                            
                        secretkey = {'\x05\x00\x00\x00'}
						
                        def without_keys(d, keys) :
                            return {x: d[x] for x in d if x not in keys}
                        execdict_new = without_keys(execdict, secretkey)
                        # print(execdict)
                        # print(execdict_new)
                        blob = blob_utilities.blob_serialize(execdict_new)
                        # print(blob)
                        bloblen = len(blob)
                        log.debug("Blob length: " + str(bloblen))
                        innerkey = binascii.a2b_hex("10231230211281239191238542314233") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        innerIV  = binascii.a2b_hex("12899c8312213a123321321321543344") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                        blob_encrypted = encryption.aes_encrypt(innerkey, innerIV, blob)
                        blob_encrypted = struct.pack("<L", bloblen) + innerIV + blob_encrypted
                        blob_signature = encryption.sign_message(innerkey, blob_encrypted)
                        blob_encrypted_len = 10 + len(blob_encrypted) + 20
                        blob_encrypted = struct.pack(">L", blob_encrypted_len) + "\x01\x45" + struct.pack("<LL", blob_encrypted_len, 0) + blob_encrypted + blob_signature
                        self.socket.send("\x00" + blob_encrypted)

                        execdict = {}
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            execdict = ast.literal_eval(userblobstr[16:len(userblobstr)])
                        for sub_dict in execdict:
                            if sub_dict == "\x07\x00\x00\x00":
                                for sub_sub_dict in execdict[sub_dict]:
                                    if execdict[sub_dict][sub_sub_dict]["\x03\x00\x00\x00"] == "\x01\x00":
                                        #execdict[sub_dict][sub_sub_dict]["\x03\x00\x00\x00"] = "\x01\x00"
                                        execdict[sub_dict][sub_sub_dict]["\x05\x00\x00\x00"] = "\x00"
                                        #execdict[sub_dict][sub_sub_dict]["\x06\x00\x00\x00"] = "\x00\x00"
                        with open("files/users/" + username + ".py", 'w') as g:
                            g.write("user_registry = " + str(execdict))

                        clientsocket.send("\x00" + blob_encrypted + blob_signature)
                elif commandcode == "\x0c" : # Get Encrypted Ticket for AppServer BEN NOTE: Not Operational
                    log.info(clientid + "Get Encrypted UserID Ticket To Send To AppServer")
                    print(binascii.b2a_hex(command))
                    clientsocket.send("\x01")
                elif commandcode == "\x0e" : # Lost Pass: Request Forgotten Password Verification Email BEN NOTE: Not Operational
                    log.info(clientid + "Lost password - Find by Username")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
						binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)
                    reply = clientsocket.recv_withlen()

                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    print(plaintext)
                    blobdict = blob_utilities.blob_unserialize(plaintext)
                    print(blobdict)
                    usernamechk = blobdict['\x01\x00\x00\x00']
                    username_str = usernamechk.rstrip('\x00')
					# BEN NOTE: Change to SQL!
                    if os.path.isfile("files/users/" + username_str + ".py") :
                        clientsocket.send("\x00")
                    else :
                        clientsocket.send("\x01")
                elif commandcode == "\x0f" : # Change Forgotten Password
                    log.info(clientid + "command: Change Forgotten Password")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
						binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)
                    reply = clientsocket.recv_withlen()

                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    if repr(steam.verify_message(key, cryptedblob)) :
                        plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                        IV = cryptedblob[4:20]
                        ciphertext = cryptedblob[20:-20]
                        plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                        plaintext = plaintext[0:plaintext_length]
                        #print(plaintext)
                        blobdict = blob_utilities.blob_unserialize(plaintext)
                        #print(blobdict)
                        usernamechk = blobdict['\x01\x00\x00\x00']
                        username_str = usernamechk.rstrip('\x00')
                        with open("files/users/" + username_str + ".py", 'r') as userblobfile:
                            userblobstr = userblobfile.read()
                            userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                        #print(userblob)
                        questionsalt = userblob['\x05\x00\x00\x00'][username_str]['\x05\x00\x00\x00']
                        #print(questionsalt)
                        clientsocket.send(questionsalt) #USER'S QUESTION SALT
                        reply2 = clientsocket.recv_withlen()

                        header = reply2[0:2]
                        enc_len = reply2[2:6]
                        zeros = reply2[6:10]
                        blob_len = reply2[10:14]
                        innerIV = reply2[14:30]
                        enc_blob = reply2[30:-20]
                        sig = reply2[-20:]
                        dec_blob = encryption.aes_decrypt(key, innerIV, enc_blob)
                        padding_byte = dec_blob[-1:]
                        padding_int = struct.unpack(">B", padding_byte)
                        unser_blob = blob_utilities.blob_unserialize(dec_blob[:-padding_int[0]])

                        if unser_blob["\x01\x00\x00\x00"] == userblob['\x05\x00\x00\x00'][username_str]['\x04\x00\x00\x00'] :
                            userblob['\x05\x00\x00\x00'][username_str]['\x01\x00\x00\x00'] = unser_blob["\x03\x00\x00\x00"]
                            userblob['\x05\x00\x00\x00'][username_str]['\x02\x00\x00\x00'] = unser_blob["\x02\x00\x00\x00"]
                            if (os.path.isfile("files/users/" + username_str + ".py")) :
                                with open("files/users/" + username_str + ".py", 'w') as userblobfile :
                                    userblobfile.write("user_registry = ")
                                    userblobfile.write(str(userblob))                              
                                log.info(clientid + "Password changed for: " + username_str)
                                clientsocket.send("\x00")
                            else :
                                log.warn(clientid + "SADB file error for: " + username_str)
                                clientsocket.send("\x01")
                        else :
                            log.warn(clientid + "Password change failed for: " + username_str)
                            clientsocket.send("\x01")
                    else :
                        log.warn(clientid + "Password change failed for: " + username_str)
                        clientsocket.send("\x01")

                    reply = {}
                    reply2 = {}
                elif commandcode == "\x10" : # Change Password
                    log.debug(clientid + "Change password")

                    ticket_full = binascii.b2a_hex(command)
                    command = ticket_full[0:2]
                    ticket_len = ticket_full[2:6]
                    tgt_ver = ticket_full[6:10]
                    data1_len = ticket_full[10:14]
                    username_len = ticket_full[314:318]
                    username = binascii.a2b_hex(ticket_full[14:14 + (int(username_len, 16) * 2)])
                    
                    log.info(clientid + "Password change requested for: " + username)
                    
                    userblob = {}
					# BEN NOTE: Change to SQL!
                    if (os.path.isfile("files/users/" + username + ".py")) :
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                    personalsalt = userblob['\x05\x00\x00\x00'][username]['\x02\x00\x00\x00']
                    # print(personalsalt)
                    clientsocket.send(personalsalt)  # NEW SALT PER USER
                    blobtext = clientsocket.recv_withlen()
                    key = binascii.a2b_hex("10231230211281239191238542314233")
                    IV = binascii.a2b_hex("12899c8312213a123321321321543344")
                    crypted_blob = blobtext[10:]
                    if repr(encryption.verify_message(key, crypted_blob)) :
                        plaintext = encryption.aes_decrypt(key, IV, crypted_blob[4:-4])
                        blob_len = int(binascii.b2a_hex(plaintext[18:19]), 16)
                        blob_len = len(plaintext) - 16 - blob_len
                        blob = blob_utilities.blob_unserialize(plaintext[16:-blob_len])
                        # print(blob)
                        # print(binascii.b2a_hex(blob["\x01\x00\x00\x00"]))
                        # print(binascii.b2a_hex(userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00']))
                        if blob["\x01\x00\x00\x00"] == userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00']:
                            userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00'] = blob["\x03\x00\x00\x00"]
                            userblob['\x05\x00\x00\x00'][username]['\x02\x00\x00\x00'] = blob["\x02\x00\x00\x00"]
							# BEN NOTE: Change to SQL!
                            if (os.path.isfile("files/users/" + username + ".py")) :
                                with open("files/users/" + username + ".py", 'w') as userblobfile :
                                    userblobfile.write("user_registry = ")
                                    userblobfile.write(str(userblob))                              
                                log.info(clientid + "Password changed for: " + username)
                                clientsocket.send("\x00")
                            else :
                                log.warn(clientid + "SADB file error for: " + username)
                                clientsocket.send("\x01")
                        else :
                            log.warn(clientid + "Password change failed for: " + username)
                            clientsocket.send("\x01")
                    else :
                        log.warn(clientid + "Password change failed for: " + username)
                        clientsocket.send("\x01")
                elif commandcode == "\x11" : # Change question
                    ticket_full = binascii.b2a_hex(command)
                    command = ticket_full[0:2]
                    ticket_len = ticket_full[2:6]
                    tgt_ver = ticket_full[6:10]
                    data1_len = ticket_full[10:14]
                    username_len = ticket_full[314:318]
                    username = binascii.a2b_hex(ticket_full[14:14 + (int(username_len, 16) * 2)])
                    
                    log.info(clientid + "Secret question change requested for: " + username)
                    
                    userblob = {}
					# BEN NOTE: Change to SQL!
                    if (os.path.isfile("files/users/" + username + ".py")) :
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                    personalsalt = userblob['\x05\x00\x00\x00'][username]['\x02\x00\x00\x00']
                    # print(personalsalt)
                    clientsocket.send(personalsalt)  # NEW SALT PER USER
                    blobtext = clientsocket.recv_withlen()
                    key = binascii.a2b_hex("10231230211281239191238542314233")
                    IV = binascii.a2b_hex("12899c8312213a123321321321543344")
                    crypted_blob = blobtext[10:]
                    if repr(encryption.verify_message(key, crypted_blob)) :
                        plaintext = encryption.aes_decrypt(key, IV, crypted_blob[4:-4])
                        blob_len = int(binascii.b2a_hex(plaintext[18:19]), 16)
                        blob_len = len(plaintext) - 16 - blob_len
                        blob = blob_utilities.blob_unserialize(plaintext[16:-blob_len])
                        # print(blob)
                        # print(binascii.b2a_hex(blob["\x01\x00\x00\x00"]))
                        # print(binascii.b2a_hex(userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00']))
                        if blob["\x01\x00\x00\x00"] == userblob['\x05\x00\x00\x00'][username]['\x01\x00\x00\x00'] :
                            userblob['\x05\x00\x00\x00'][username]['\x03\x00\x00\x00'] = blob["\x02\x00\x00\x00"]
                            userblob['\x05\x00\x00\x00'][username]['\x04\x00\x00\x00'] = blob["\x04\x00\x00\x00"]
                            userblob['\x05\x00\x00\x00'][username]['\x05\x00\x00\x00'] = blob["\x03\x00\x00\x00"]
							# BEN NOTE: Change to SQL!
                            if (os.path.isfile("files/users/" + username + ".py")) :
                                with open("files/users/" + username + ".py", 'w') as userblobfile :
                                    userblobfile.write("user_registry = ")
                                    userblobfile.write(str(userblob))                              
                                log.info(clientid + "Secret question changed for: " + username)
                                clientsocket.send("\x00")
                            else :
                                log.warn(clientid + "SADB file error for: " + username)
                                clientsocket.send("\x01")
                        else :
                            log.warn(clientid + "Secret question change failed for: " + username)
                            clientsocket.send("\x01")
                    else :
                        log.warn(clientid + "Secret question change failed for: " + username)
                        clientsocket.send("\x01")
                elif commandcode == "\x12" : # Change Email
                    log.info(clientid + "Change Email")
                    ticket_full = binascii.b2a_hex(command)
                    command = ticket_full[0:2]
                    ticket_len = ticket_full[2:6]
                    tgt_ver = ticket_full[6:10]
                    data1_len = ticket_full[10:14]
                    data1_len = int(data1_len, 16) * 2
                    userIV = binascii.a2b_hex(ticket_full[14 + data1_len:14 + data1_len + 32])
                    username_len = ticket_full[314:318]
                    username = binascii.a2b_hex(ticket_full[14:14 + (int(username_len, 16) * 2)])
                    ticket_len = int(ticket_len, 16) * 2
                    ticket = ticket_full[2:ticket_len + 2]
                    postticketdata = ticket_full[2 + ticket_len + 4:]
                    key = binascii.a2b_hex("10231230211281239191238542314233")
                    iv = binascii.a2b_hex(postticketdata[0:32])
                    encdata_len = int(postticketdata[36:40], 16) * 2
                    encdata = postticketdata[40:40 + encdata_len]
                    decodedmessage = binascii.b2a_hex(encryption.aes_decrypt(key, iv, binascii.a2b_hex(encdata)))
                    decodedmessage = binascii.a2b_hex(decodedmessage)
                    username_len_new = struct.unpack("<H", decodedmessage[0:2])
                    username_len_new = (2 + username_len_new[0]) * 2
                    header = username_len_new + 8
                    blob_len = struct.unpack("<H", decodedmessage[header + 2:header + 4])
                    blob_len = (blob_len[0])
                    blob = (decodedmessage[header:header + blob_len])
                    padding_byte = blob[-1:]
                    padding_int = struct.unpack(">B", padding_byte)
                    new_email_addr = blob[:-padding_int[0]]
                    new_email_addr = new_email_addr + "\x00"

                    userblob = {}
                    execdict_new = {}
					# BEN NOTE: change to sql!
                    if (os.path.isfile("files/users/" + username + ".py")):
                        with open("files/users/" + username + ".py", 'r') as f:
                            userblobstr = f.read()
                            userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                    personalsalt = userblob['\x05\x00\x00\x00'][username]['\x02\x00\x00\x00']
                    new_email = {}
                    new_email = {"\x0b\x00\x00\x00": new_email_addr}
                    userblob.update(new_email)
                    with open("files/users/" + username + ".py", 'w') as g:
                        g.write("user_registry = " + str(userblob))
                    secretkey = {'\x05\x00\x00\x00'}

                    def without_keys(d, keys):
                        return {x: d[x] for x in d if x not in keys}
                    execdict_new = without_keys(userblob, secretkey)
                    # print(userblob)
                    # print(execdict_new)
                    blob = blob_utilities.blob_serialize(execdict_new)
                    # print(blob)
                    bloblen = len(blob)
                    log.debug("Blob length: " + str(bloblen))
                    innerkey = binascii.a2b_hex("10231230211281239191238542314233") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                    #innerIV  = binascii.a2b_hex("12899c8312213a123321321321543344") #ONLY FOR BLOB ENCRYPTION USING AES-CBC
                    innerIV = userIV
                    blob_encrypted = encryption.aes_encrypt(innerkey, innerIV, blob)
                    blob_encrypted = struct.pack("<L", bloblen) + innerIV + blob_encrypted
                    blob_signature = encryption.sign_message(innerkey, blob_encrypted)
                    blob_encrypted_len = 10 + len(blob_encrypted) + 20
                    blob_encrypted = struct.pack(">L", blob_encrypted_len) + "\x01\x45" + struct.pack("<LL", blob_encrypted_len, 0) + blob_encrypted
                    ticket = ticket + blob_encrypted
                    ticket_signed = ticket + encryption.sign_message(innerkey, ticket)
                    clientsocket.send("\x00" + blob_encrypted + blob_signature)
                elif commandcode == "\x13" : # Verify Email   BEN NOTE: Not Operational
                    print("verify Email")
                    clientsocket.send("\x01")
                elif commandcode == "\x14" : # Request verification Email    BEN NOTE: Not Operational,  Does not expect response.
                    print("Requested Verification Email")
                    clientsocket.send("\x01")
                elif commandcode == "\x15" : # Update Account Billing Info   BEN NOTE: Not Operational,  Does not expect response.
                    print("Update Account Billing Information")
                    clientsocket.send("\x01")
                elif commandcode == "\x16" : # Update Subscription Billing Info   BEN NOTE: Not Operational,  Does not expect response.
                    print("Update Subscription Billing Information")
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
					binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)
                    reply = clientsocket.recv_withlen()

                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    # print(plaintext)
                    blobdict = blob_utilities.blob_unserialize(plaintext)
                    # print(blobdict)
                    usernamechk = blobdict['\x01\x00\x00\x00']
                    username_str = usernamechk.rstrip('\x00')
					
                    with open("files/users/" + username_str + ".py", 'r') as userblobfile:
                        userblobstr = userblobfile.read()
                        userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
						
                    # print(str(userblob))
                    personalsalt = userblob['\x05\x00\x00\x00'][username_str]['\x02\x00\x00\x00']
                    # print(personalsalt)
                    clientsocket.send(personalsalt)  # NEW SALT PER USER

                    reply2 = clientsocket.recv_withlen()

                    RSAdata = reply2[2:130]
                    datalength = struct.unpack(">L", reply2[130:134])[0]
                    cryptedblob_signature = reply2[134:136]
                    cryptedblob_length = reply2[136:140]
                    cryptedblob_slack = reply2[140:144]
                    cryptedblob = reply2[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    #print blob_utilities.blob_unserialize(plaintext)
                elif commandcode == "\x1b" : # Unknown Packet   BEN NOTE: Not Operational
                    log.info(clientid + "Unknown Packet (0x1B) [Not Functional]")
                    clientsocket.send("\x00")       
                elif commandcode == "\x1c" : # Change Account Name
                    log.info(clientid + "Change Account Name")
                    print(binascii.b2a_hex(command))
                    clientsocket.send("\x01")   
                elif commandcode == "\x1d" : # Create Account: Is Name in use
                    log.info(clientid + "command: query account name already in use")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
					binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)

                    reply = clientsocket.recv_withlen()
                
                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    # print(plaintext)
                    plainblob = blob_utilities.blob_unserialize(plaintext)
                    # print(plainblob)
                    username = plainblob['\x01\x00\x00\x00']
                    username_str = username.rstrip('\x00')
                    # print(len(username_str))
                    log.info(clientid + "New user: check username exists: " + username_str)
					
                    if auth_utilities.check_username_exists(username_str): #set second arg to 1 to indicate we are just checking for name
                        log.warn(clientid + "New user: username already exists")
                        clientsocket.send("\x01")  # Username in use!
                    else:
                        log.info(clientid + "New user: username not in use")
                        clientsocket.send("\x00")  # Username is not in use
                elif commandcode == "\x1e" : # Generate Suggested Name   BEN NOTE: Not Operational     
                    log.info(clientid + "command: Generate Suggested Name [Not Implemented]")
                elif commandcode == "\x1f" : # ProtocolSubroutine_ReceiveEncryptedAccountNames   BEN NOTE: Not Operational          
                    log.info(clientid + "ProtocolSubroutine_ReceiveEncryptedAccountNames [Not Functional]")
                    clientsocket.send("\x02")
                elif commandcode == "\x20" : # Check email - password reset
                    log.info(clientid + "Password reset by email")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = steam.rsa_sign_message_1024(steam.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    
                    clientsocket.send(reply)
                    reply = clientsocket.recv_withlen()
                    
                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]

                    key = steam.get_aes_key(RSAdata, steam.network_key)
                    log.debug("Message verification:" + repr(steam.verify_message(key, cryptedblob)))
                    if repr(encryption.verify_message(key, cryptedblob)) :
                        plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                        IV = cryptedblob[4:20]
                        ciphertext = cryptedblob[20:-20]
                        plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                        plaintext = plaintext[0:plaintext_length]
                        #print(plaintext)
                        blobdict = blob_utilities.blob_unserialize(plaintext)
                        #print(blobdict)
                        emailchk = blobdict['\x01\x00\x00\x00']
                        email_str = emailchk.rstrip('\x00')
                        email_found = False
                        for file in os.listdir("files/users/"):
                            if file.endswith("py"):
                                with open("files/users/" + file, 'r') as f:
                                    userblobstr = f.read()
                                    userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                                email_addr = userblob['\x0b\x00\x00\x00']
                                if email_addr.rstrip('\x00') == email_str :
                                    email_found = True
                                    break
                        if email_found :
                            clientsocket.send("\x00")
                        else :
                            clientsocket.send("\x01")
                elif commandcode == "\x21" : # Check key - password reset
                    log.info(clientid + "Password reset by CD key")
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(steam.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)
                    reply = clientsocket.recv_withlen()

                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]

                    key = encryption.get_aes_key(RSAdata, steam.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    if repr(encryption.verify_message(key, cryptedblob)) :
                        plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                        IV = cryptedblob[4:20]
                        ciphertext = cryptedblob[20:-20]
                        plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                        plaintext = plaintext[0:plaintext_length]
                        #print(plaintext)
                        blobdict = blob_utilities.blob_unserialize(plaintext)
                        #print(blobdict)
                        keychk = blobdict['\x01\x00\x00\x00']
                        key_str = keychk.rstrip('\x00')
                        key_found = False
                        for file in os.listdir("files/users/"):
                            if file.endswith("py"):
                                with open("files/users/" + file, 'r') as f:
                                    userblobstr = f.read()
                                    userblob = ast.literal_eval(userblobstr[16:len(userblobstr)])
                                for sub in userblob["\x0f\x00\x00\x00"] :
                                    for prodcdkey in userblob["\x0f\x00\x00\x00"][sub]["\x01\x00\x00\x00"] :
                                        if prodcdkey == "\x06" :
                                            key = userblob["\x0f\x00\x00\x00"][sub]["\x02\x00\x00\x00"]["\x02\x00\x00\x00"][:-1]
                                            if key == key_str :
                                                key_found = True
                                                break
                        if key_found :
                            clientsocket.send("\x00")
                        else :
                            clientsocket.send("\x01")
                elif commandcode == "\x22" : # Get Number of Accounts Associated With Email 
                    log.info( clientid + "command: Get Number Of Accounts Associated With Email")
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
						binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("9525173d72e87cbbcbdc86146587aebaa883ad448a6f814dd259bff97507c5e000cdc41eed27d81f476d56bd6b83a4dc186fa18002ab29717aba2441ef483af3970345618d4060392f63ae15d6838b2931c7951fc7e1a48d261301a88b0260336b8b54ab28554fb91b699cc1299ffe414bc9c1e86240aa9e16cae18b950f900f") + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)

                    reply = clientsocket.recv_withlen()
                
                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    # print(plaintext)
                    plainblob = blob_utilities.blob_unserialize(plaintext)
                    # print(plainblob)
                    email = plainblob['\x01\x00\x00\x00']
                    email_str = email.rstrip('\x00')
                    # print(len(username_str))
                    log.info( clientid + "Get Number of Accounts Associated with email: " + email_str)
                    
                    clientsocket.send("\x00"+auth_utilities.decimal_to_4byte_hex(int(auth_utilities.count_email_in_files(email_str))))
                elif commandcode == "\x23" : # Acknowledge Subscription Receipt. Does not expect response.
                    log.info(
                        clientid + "Client Acknowledged Subscription Receipt")
                    clientsocket.close()
                else:
                    # This is cheating. I've just cut'n'pasted the hex from the network_key. FIXME
                    #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                    BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + \
                        binascii.a2b_hex(
                            self.config["net_key_n"][2:]) + "\x02\x01\x11"
                    signature = encryption.rsa_sign_message_1024(
                        encryption.main_key_sign, BERstring)
                    reply = struct.pack(">H", len(
                        BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature
                    clientsocket.send(reply)

                    reply = clientsocket.recv_withlen()
                
                    RSAdata = reply[2:130]
                    datalength = struct.unpack(">L", reply[130:134])[0]
                    cryptedblob_signature = reply[134:136]
                    cryptedblob_length = reply[136:140]
                    cryptedblob_slack = reply[140:144]
                    cryptedblob = reply[144:]
                
                    key = encryption.get_aes_key(RSAdata, encryption.network_key)
                    log.debug("Message verification:" + repr(encryption.verify_message(key, cryptedblob)))
                    plaintext_length = struct.unpack("<L", cryptedblob[0:4])[0]
                    IV = cryptedblob[4:20]
                    ciphertext = cryptedblob[20:-20]
                    plaintext = encryption.aes_decrypt(key, IV, ciphertext)
                    plaintext = plaintext[0:plaintext_length]
                    #print blob_utilities.blob_unserialize(plaintext)
                
                    clientsocket.send("\x00")
                #log.warning(clientid + "Invalid command length: " + str(len(command)))
        else :
            data = clientsocket.recv(65535)
            log.warning(clientid + "Invalid command: " + binascii.b2a_hex(command[1:5]))
            log.warning(clientid + "Extra data:", binascii.b2a_hex(data))

        clientsocket.close()
        log.info(clientid + "Disconnected from Auth Server")
