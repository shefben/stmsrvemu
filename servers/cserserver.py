import binascii
import csv
import datetime
import logging
import os
import os.path
import struct
import time
from CryptICE import IceKey
# from utilities.ICE_cipher import IceKey
from builtins import range
from builtins import str

from utilities.networkbuffer import NetworkBuffer
from utilities.networkhandler import UDPNetworkHandler


def int_wrapper(value) :
    try :
        val1 = int(value, base=16)
        return val1
    except (ValueError, TypeError) :
        return 0


class CSERServer(UDPNetworkHandler) :
    q_key = [54, 175, 165, 5, 76, 251, 29, 113]

    o1_key = [200, 145, 255, 149, 195, 190, 108, 243]
    o2_key = [200, 145, 10, 149, 195, 190, 108, 243]
    g_key = [27, 200, 13, 14, 83, 45, 184, 54]

    def __init__(self, port, config) :
        self.server_type = "CSERServer"
        super(CSERServer, self).__init__(config, int(port), self.server_type)  # Create an instance of NetworkHandler

    def handle_client(self, data, address) :
        log = logging.getLogger(self.server_type)
        # Process the received packet
        clientid = str(address) + ": "
        log.info(clientid + "Connected to CSER Server")
        log.debug(clientid + ("Received message: %s, from %s" % (repr(data), address)))
        ipstr = str(address)
        ipstr1 = ipstr.split('\'')
        ipactual = ipstr1[1]
        if data.startswith(b"e") :  # 65
            message = binascii.b2a_hex(data)
            keylist = list(range(7))
            vallist = list(range(7))
            keylist[0] = "SuccessCount"
            keylist[1] = "UnknownFailureCount"
            keylist[2] = "ShutdownFailureCount"
            keylist[3] = "UptimeCleanCounter"
            keylist[4] = "UptimeCleanTotal"
            keylist[5] = "UptimeFailureCounter"
            keylist[6] = "UptimeFailureTotal"
            try :
                os.mkdir("clientstats")
            except OSError as error :
                log.debug("Client stats dir already exists")
            if message.startswith(b"650a01537465616d2e657865") :  # Steam.exe
                vallist[0] = str(int(message[24 :26], base=16))
                vallist[1] = str(int(message[26 :28], base=16))
                vallist[2] = str(int(message[28 :30], base=16))
                vallist[3] = str(int(message[30 :32], base=16))
                vallist[4] = str(int(message[32 :34], base=16))
                vallist[5] = str(int(message[34 :36], base=16))
                vallist[6] = str(int(message[36 :38], base=16))
                f = open("clientstats\\" + str(ipactual) + ".steamexe.csv", "w")
                f.write(str(binascii.a2b_hex(message[6 :24])))
                f.write("\n")
                f.write(keylist[0] + "," + keylist[1] + "," + keylist[2] + "," + keylist[3] + "," + keylist[4] + "," +
                        keylist[5] + "," + keylist[6])
                f.write("\n")
                f.write(vallist[0] + "," + vallist[1] + "," + vallist[2] + "," + vallist[3] + "," + vallist[4] + "," +
                        vallist[5] + "," + vallist[6])
                f.close( )
                log.info(clientid + "Received client stats")
        elif data.startswith(b"c") :  # 63
            message = binascii.b2a_hex(data)
            keylist = list(range(13))
            vallist = list(range(13))
            keylist[0] = "Unknown1"
            keylist[1] = "Unknown2"
            keylist[2] = "ModuleName"
            keylist[3] = "FileName"
            keylist[4] = "CodeFile"
            keylist[5] = "ThrownAt"
            keylist[6] = "Unknown3"
            keylist[7] = "Unknown4"
            keylist[8] = "AssertPreCondition"
            keylist[9] = "Unknown5"
            keylist[10] = "OsCode"
            keylist[11] = "Unknown6"
            keylist[12] = "Message"
            try :
                os.mkdir("crashlogs")
            except OSError as error :
                log.debug("Client crash reports dir already exists")
            templist = binascii.a2b_hex(message)
            templist2 = templist.split(b'\x00')
            # try :
            vallist[0] = str(int_wrapper(binascii.b2a_hex(templist2[0][2 :4])))
            vallist[1] = str(int_wrapper(binascii.b2a_hex(templist2[1])))
            vallist[2] = str(templist2[2])
            vallist[3] = str(templist2[3])
            vallist[4] = str(templist2[4])
            vallist[5] = str(int_wrapper(binascii.b2a_hex(templist2[5])))
            vallist[6] = str(int_wrapper(binascii.b2a_hex(templist2[7])))
            vallist[7] = str(int_wrapper(binascii.b2a_hex(templist2[10])))
            vallist[8] = str(templist2[13])
            vallist[9] = str(int_wrapper(binascii.b2a_hex(templist2[14])))
            vallist[10] = str(int_wrapper(binascii.b2a_hex(templist2[15])))
            vallist[11] = str(int_wrapper(binascii.b2a_hex(templist2[18])))
            vallist[12] = str(templist2[23])
            timestamp = datetime.datetime.now( ).strftime("%Y-%m-%d_%H-%M-%S")
            filename = "crashlogs\\" + str(ipactual) + "_" + timestamp + ".csv"

            f = open(filename, "w")
            f.write("SteamExceptionsData")
            f.write("\n")
            f.write(
                    keylist[0] + "," + keylist[1] + "," + keylist[2] + "," + keylist[3] + "," + keylist[4] + "," +
                    keylist[
                        5] + "," + keylist[6] + "," + keylist[7] + "," + keylist[8] + "," + keylist[9] + "," + keylist[
                        10] + "," + keylist[11] + "," + keylist[12])
            f.write("\n")
            f.write(
                    vallist[0] + "," + vallist[1] + "," + vallist[2] + "," + vallist[3] + "," + vallist[4] + "," +
                    vallist[
                        5] + "," + vallist[6] + "," + vallist[7] + "," + vallist[8] + "," + vallist[9] + "," + vallist[
                        10] + "," + vallist[11] + "," + vallist[12])
            f.close( )
            log.info(clientid + "Received client crash report")
            # except :
            # log.debug(clientid + "Failed to receive client crash report")

            # d =  message type
            # then 1 = request denied, invalid message protocol
            # 2 = server accepts minidump, so client will send it now

        elif data.startswith(b"q") :  # 71
            ice = IceKey(1, [27, 200, 13, 14, 83, 45, 184, 54])
            log.info("Received encrypted ICE client stats")
            # C2M_BUGREPORT details
            #     u8(C2M_UPLOADDATA_PROTOCOL_VERSION) == 1
            #     u16(encryptedlength)
            #     remainder=encrypteddata

            # encrypted payload:
            #     byte(corruptionid)
            #     byte(protocolid) // C2M_UPLOADDATA_DATA_VERSION == 1
            #     string(tablename 40)
            #     u8(numvalues)
            #     for each value:
            #         string(fieldname 32)
            #         string(value 128)

            # Assuming you have received the encrypted data in the 'data' variable
            # Assuming you have received the encrypted data in the 'data' variable
            data_bin = binascii.unhexlify(data[5 :])
            data_length = len(data_bin)

            # Create a NetworkBuffer instance with the decrypted data
            buffer = NetworkBuffer(data_bin)

            # Extract information
            protocol_version = buffer.extract_u8( )
            encrypted_length = buffer.extract_u16( )

            # Decrypt the remainder of the data
            decrypted = ice.Decrypt(buffer.extract_buffer(encrypted_length))

            # Create a new NetworkBuffer instance for the decrypted data
            buffer = NetworkBuffer(decrypted)

            # Create a dictionary to store the extracted information
            info = {
                "protocol_version" : protocol_version,
                "encrypted_length" : encrypted_length,
            }

            # Extract encrypted payload
            corruption_id = buffer.extract_u8( )
            protocol_id = buffer.extract_u8( )
            tablename = buffer.extract_buffer(40).rstrip(b'\x00')
            num_values = buffer.extract_u8( )

            values = []
            for _ in range(num_values) :
                fieldname = buffer.extract_buffer(32).rstrip(b'\x00')
                value = buffer.extract_buffer(128).rstrip(b'\x00')
                values.append((fieldname, value))

            # Add the extracted values to the dictionary
            info["corruption_id"] = corruption_id
            info["protocol_id"] = protocol_id
            info["tablename"] = tablename
            info["num_values"] = num_values
            info["values"] = values

            # Define the directory for saving CSV files
            save_directory = './clientstats'

            # Create the directory if it doesn't exist
            if not os.path.exists(save_directory) :
                os.makedirs(save_directory)

            # Generate the CSV filename
            filename = os.path.join(save_directory, address[0] + '.bugreport#' + str(decrypted[0]) + '.csv')

            # Save the information to a CSV file
            with open(filename, 'w', newline='') as csv_file :
                csv_writer = csv.writer(csv_file)
                for field, val in values :
                    csv_writer.writerow([field, val])

            """//M2C_ACKUPLOADDATA details
		    u8(protocol okay (bool))"""

            self.serversocket.sendto(b"\xFF\xFF\xFF\xFF\x72\x01",
                                     address)  # 72 = r command and the next byte is a bool, ok = 1, bad = 0

        elif data.startswith(b"a") :  # 61
            log.info("Received app download stats - INOP")
            self.serversocket.sendto(b"\xFF\xFF\xFF\xFFb\x01",
                                     address)
        elif data.startswith(b"o") :
            log.info("Received bug report - INOP")
            """		// C2M_BUGREPORT details
            //		u8(C2M_BUGREPORT_PROTOCOL_VERSION) = 1 2 or 3
            //		u16(encryptedlength)
            //		remainder=encrypteddata

            // encrypted payload:
            //		byte corruptionid = 1
            //		u32(buildnumber)
            //		string(exename 64)
            //		string(gamedir 64)
            //		string(mapname 64)
            //		u32 RAM
            //		u32 CPU
            //		string(processor)
            //		u32 DXVerHigh
            //		u32 DXVerLow
            //		u32	DXVendorID
            //		u32 DXDeviceID
            //		string(OSVer)
            
            // Version 2+:
            //	{
            //			reporttype(char 32)
            //			email(char 80)
            //			accountname(char 80)
            //	}

            // Version 3+
            //  {
            //			userid( sizeof( TSteamGlobalUserID ) )
            //  }

            // --- all versions
            //		string(title 128)
            //		u32(.zip file size, or 0 if none available)
            //		u32(text length > max 1024)
            //		text(descriptive text -- capped to text length bytes)"""

            """ // M2C_ACKBUGREPORT details
            //	u8(protocol okay (bool))
            //	u8(BR_NO_FILES or BR_REQEST_FILES )
            //  iff BR_REQEST_FILES then add:
            //    u32(harvester ip address)
            //	  u16(harvester port #)
            //	  u32(upload context id)
            """
            self.serversocket.sendto(b"\xFF\xFF\xFF\xFF\x71\x01", address)
        elif data.startswith(b"i") :  # 69
            log.info("Received unknown stats - INOP")
            self.serversocket.sendto(b"\xFF\xFF\xFF\xFFj\x01",
                                     address)
        elif data.startswith(b"k") :  # 6b
            log.info("Received game statistics stats - INOP")  # respond with lowercase L
            self.serversocket.sendto(b"\xFF\xFF\xFF\xFFl\x01",
                                     address)
        elif data.startswith(b"m") :
            """	
            // C2M_PHONEHOME
            //	u8( C2M_PHONEHOME_PROTOCOL_VERSION )
            //	u32( sessionid ) or 0 to request a new sessionid
            //  u16(encryptedlength)
            //  remainder = encrypteddata:
            // u8 corruption id == 1
            //  string build unique id
            //  string computername
            //	string username
            //  string gamedir
            //  float( enginetimestamp )
            //  u8 messagetype:
            //    1:  engine startup 
            //    2:  engine shutdown
            //    3:  map started + mapname
            //    4:  map finished + mapname
            //	string( mapname )
            """
            ice = IceKey(1, [27, 200, 13, 14, 83, 45, 184, 54])  # unknown key, this is probably incorrect

            # Assuming you have received the encrypted data in the 'data' variable
            data_bin = binascii.unhexlify(data[5 :])
            data_length = len(data_bin)

            # Create a NetworkBuffer instance with the decrypted data
            buffer = NetworkBuffer(data_bin)

            # Extract information
            protocol_version = buffer.extract_u8( )
            session_id = buffer.extract_u32( )
            encrypted_length = buffer.extract_u16( )
            encrypted_data = buffer.extract_buffer(encrypted_length)

            # Decrypt the remainder of the data
            decrypted = ice.Decrypt(encrypted_data)

            # Create a new NetworkBuffer instance for the decrypted data
            buffer = NetworkBuffer(decrypted)

            # Extract the remaining information
            corruption_id = buffer.extract_u8( )
            unique_id = buffer.extract_buffer( ).rstrip(b'\x00')
            computer_name = buffer.extract_buffer( ).rstrip(b'\x00')
            username = buffer.extract_buffer( ).rstrip(b'\x00')
            game_dir = buffer.extract_buffer( ).rstrip(b'\x00')
            engine_timestamp = struct.unpack('f', buffer.extract_buffer(4))[0]
            message_type = buffer.extract_u8( )

            # Log the received data
            log.info("Received Phone Home - INOP")

            # Prepare the extracted data
            extracted_data = {
                "protocol_version" : protocol_version,
                "session_id"       : session_id,
                "encrypted_length" : encrypted_length,
                "corruption_id"    : corruption_id,
                "unique_id"        : unique_id,
                "computer_name"    : computer_name,
                "username"         : username,
                "game_dir"         : game_dir,
                "engine_timestamp" : engine_timestamp,
                "message_type"     : message_type
            }

            # Generate a filename based on the IP address and timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "clientstats/{}.{}.phonehome.txt".format(address, timestamp)

            # Write the extracted data to a file
            with open(filename, "w") as file :
                for key, value in list(extracted_data.items( )) :
                    file.write("\n{} : {}".format(key, value))

                self.serversocket.sendto(b"\xFF\xFF\xFF\xFF\x6E\x01" + session_id, address)  # random session id, 321

        elif data.startswith(b"g") :  # survey response
            #\x01 decryption OK
            # 84af0a4be34af5f0eea515a1153be52a\x00 clientid?
            # \xff\x07\x00\x00 ram size
            # \xb9\x0b\x00\x00 processor speed in mhz Speed:
            # \x00\x00\x00\x00
            # \x20\x03 ScreenSize
            # \x00\x00
            # \x03 RenderMode  02 = opengl, 03 = d3d, 01 = software?
            # \x10\x00 Bit Depth
            # nvldumd.dll\x00 driver
            # \x00
            # NVIDIA GeForce RTX 3050\x00
            # \x00\x00
            # \x1f\x00 minor Video Card Version
            # \x81\x0e middle major Video Card Version
            # \x0f\x00 major Video Card Version
            # \xde\x10\x00\x00 vendor id
            # \x07\x25 DeviceID:
            # \x00
            # \x00 HyperThreading:  Unsupported ??
            # \x01 RDTSC:  Supported
            # \x01 CMOV:  Supported
            # \x01 FCMOV:  Supported
            # \x01 SSE:  Supported
            # \x01 SSE2:  Suppo
            # \x00 3DNOW:
            # \x01  NTFS:  Supported ??
            # GenuineIntel\x00 Vendor
            # \x08  8 logical proccessors
            # \x08  8 physical processors
            # \x00\x00\x00\x00\x00\x00
            #   (Build 9200) \x00 Windows Version (2 spaces prior)
            # \x38\xa8\xc0\x00 IP Address
            # \x02   Media Type  01 = cdrom, 02 = dvd
            # \x3d\xe7\x09\x00 Largest Free Hard Disk Block
            # \xbb\x7a\x6d\x00 Total Hard Disk Space Available
            # \x00\x00\x00\x00
            # \x00
            # \x00\x00
            """ice = IceKey(1, [27, 200, 13, 14, 83, 45, 184, 54])
            data_bin = binascii.unhexlify(data[5:])
            decrypted = ice.Decrypt(data_bin)

            print(repr(decrypted))

            ip_address = address[0]
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = "clientstats/{}.{}.hwsurvey.txt".format(ip_address, timestamp)

            
            with open(filename, "w") as f :
                f.write(decrypted)
                f.close( )"""
            self.serversocket.sendto(b"\xFF\xFF\xFF\xFF\x68\x01\x00\x00\x00" + b"thank you\n\0", address)
        else :
            log.info("Unknown CSER command: %s" % data)