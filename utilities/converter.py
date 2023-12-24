

import binascii
import logging
import os
import struct
import time

from utilities.manifests import Manifest

import globalvars
from config import get_config as read_config
from gcf_to_storage import gcf2storage

config = read_config( )


def convertgcf() :
    log = logging.getLogger("converter")
    if config["public_ip"] != "0.0.0.0" :
        server_ip = config["public_ip"]
    else:
        server_ip = config["server_ip"]
    server_ip = server_ip.encode("latin-1")
    makeenc = Manifest( )
    # makeenc.make_encrypted("files/convert/206_1.manifest")
    # makeenc.make_encrypted("files/convert/207_1.manifest")
    # makeenc.make_encrypted("files/convert/208_1.manifest")
    # makeenc.make_encrypted("files/convert/221_0.manifest")
    # makeenc.make_encrypted("files/convert/281_0.manifest")
    for filename in os.listdir("files/convert/") :
        if str(filename.endswith(".gcf")) :
            # dirname = filename[0:-4]
            with open("files/convert/" + filename, "rb") as g :
                h = g.read(20)

            depotid = struct.unpack("<L", h[12 :16])[0]
            versionid = struct.unpack("<L", h[16 :20])[0]

            dirname = str(depotid) + "_" + str(versionid)
            if not os.path.isfile("files/cache/" + dirname + "/" + dirname + ".manifest") :
                log.info("Found " + filename + " to convert")
                log.info("Neutering Valve strings...")
                log.debug("****************************************")
                g = open("files/convert/" + filename, "rb")
                file = g.read( )
                origsize = len(file)
                g.close( )
                if config["public_ip"] != "0.0.0.0" :
                    for (search, replace, info) in globalvars.replace_string(False):
                        fulllength = len(search)
                        newlength = len(replace)
                        missinglength = fulllength - newlength
                        if missinglength < 0 :
                            log.debug("WARNING: Cannot replace " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ) + " as it's too long")
                        elif missinglength == 0 :
                            file = file.replace(search, replace)
                            log.debug("Replaced " + info.decode( ))  # + " " + search.decode() + " with " + replace.decode())
                        else :
                            file = file.replace(search, replace + (b'\x00' * missinglength))
                            log.debug("Replaced " + info.decode( ))  # + " " + search + " with " + replace)
                else :
                    for (search, replace, info) in globalvars.replace_string(True) :
                        fulllength = len(search)
                        newlength = len(replace)
                        missinglength = fulllength - newlength
                        if missinglength < 0 :
                            log.debug("WARNING: Cannot replace due to length mismatch")
                        else :
                            file = file.replace(search, replace + (b'\x00' * missinglength))
                            try :
                                log.debug("Replaced " + info.decode('utf-8') + " with " + replace.decode('utf-8'))
                            except UnicodeDecodeError :
                                # Fallback to ISO-8859-1 or log binary data directly
                                log.debug("Replaced binary data due to decode error")

                search = b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + \
                         config["dir_server_port"] + " "
                else :
                    ip = config["server_ip"] + ":" + config["dir_server_port"] + " "
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced directory server IP group 1")

                search = b"207.173.177.11:27030 207.173.177.12:27030"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":" + config["dir_server_port"] + " " + config["server_ip"] + ":" + \
                         config["dir_server_port"] + " "
                else :
                    ip = config["server_ip"] + ":" + config["dir_server_port"] + " "
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced directory server IP group 5")

                search = b"hlmaster1.hlauth.net:27010"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":27010"
                else :
                    ip = config["server_ip"] + ":27010"
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced default HL Master server DNS")

                search = b"207.173.177.11:27010"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":27010"
                else :
                    ip = config["server_ip"] + ":27010"
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced default HL Master server IP 1")

                search = b"207.173.177.12:27010"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":27010"
                else :
                    ip = config["server_ip"] + ":27010"
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced default HL Master server IP 2")

                search = b"207.173.177.11:27011"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":27011"
                else :
                    ip = config["server_ip"] + ":27011"
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced default HL2 Master server IP 1")

                search = b"207.173.177.12:27011"
                if config["public_ip"] != "0.0.0.0" :
                    ip = config["public_ip"] + ":27011"
                else :
                    ip = config["server_ip"] + ":27011"
                searchlength = len(search)
                iplength = len(ip)
                numtoreplace = searchlength // iplength
                ips = ip * numtoreplace
                replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                if file.find(search) != -1 :
                    file = file.replace(search, replace)
                    log.debug("Replaced default HL2 Master server IP 2")

                search = binascii.a2b_hex(
                        b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223022")
                replace = binascii.a2b_hex(
                        b"2245787069726174696F6E59656172436F6D626F220D0A09092278706F7322090922323632220D0A09092279706F7322090922313634220D0A09092277696465220909223636220D0A09092274616C6C220909223234220D0A0909226175746F526573697A652209092230220D0A09092270696E436F726E65722209092230220D0A09092276697369626C652209092231220D0A090922656E61626C65642209092231220D0A090922746162506F736974696F6E2209092234220D0A0909227465787448696464656E2209092230220D0A0909226564697461626C65220909223122")
                file = file.replace(search, replace)
                log.debug("Replaced CC expiry date field")

                if config["tracker_ip"] != "0.0.0.0" :
                    search = b"tracker.valvesoftware.com:1200"
                    ip = config["tracker_ip"] + ":1200"
                    searchlength = len(search)
                    iplength = len(ip)
                    numtoreplace = searchlength // iplength
                    ips = ip * numtoreplace
                    replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                    if file.find(search) != -1 :
                        file = file.replace(search, replace)
                        log.debug("Replaced Tracker Chat server DNS")

                if config["tracker_ip"] != "0.0.0.0" :
                    search = b'"207.173.177.42:1200"'
                    ip = '"' + config["tracker_ip"] + ':1200"'
                    searchlength = len(search)
                    iplength = len(ip)
                    numtoreplace = searchlength // iplength
                    ips = ip * numtoreplace
                    replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                    if file.find(search) != -1 :
                        file = file.replace(search, replace)
                        log.debug("Replaced Tracker Chat server 1")

                if config["tracker_ip"] != "0.0.0.0" :
                    search = b'"207.173.177.43:1200"'
                    ip = '"' + config["tracker_ip"] + ':1200"'
                    searchlength = len(search)
                    iplength = len(ip)
                    numtoreplace = searchlength // iplength
                    ips = ip * numtoreplace
                    replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                    if file.find(search) != -1 :
                        file = file.replace(search, replace)
                        log.debug("Replaced Tracker Chat server 2")

                if config["tracker_ip"] != "0.0.0.0" :
                    search = b'"207.173.177.44:1200"'
                    ip = '"' + config["tracker_ip"] + ':1200"'
                    searchlength = len(search)
                    iplength = len(ip)
                    numtoreplace = searchlength // iplength
                    ips = ip * numtoreplace
                    replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                    if file.find(search) != -1 :
                        file = file.replace(search, replace)
                        log.debug("Replaced Tracker Chat server 3")

                if config["tracker_ip"] != "0.0.0.0" :
                    search = b'"207.173.177.45:1200"'
                    ip = '"' + config["tracker_ip"] + ':1200"'
                    searchlength = len(search)
                    iplength = len(ip)
                    numtoreplace = searchlength // iplength
                    ips = ip * numtoreplace
                    replace = ips.encode('utf-8') + (b'\x00' * (searchlength - len(ips)))
                    if file.find(search) != -1 :
                        file = file.replace(search, replace)
                        log.debug("Replaced Tracker Chat server 4")

                for extraip in globalvars.extraips :
                    loc = file.find(extraip)
                    if loc != -1 :
                        if config["public_ip"] != "0.0.0.0" :
                            server_ip = config["public_ip"]
                            replace_ip = server_ip + (b'\x00' * (searchlength - len(server_ip)))
                            file = file[:loc] + replace_ip + file[loc + 16 :]
                            log.debug("Found and replaced IP %s at location %08x" % (extraip.decode( ), loc))
                            if len(file) != origsize :
                                raise Exception("SIZE MISMATCH")
                        else :
                            server_ip = config["server_ip"]
                            replace_ip = server_ip + (b'\x00' * (searchlength - len(server_ip)))
                            file = file[:loc] + replace_ip + file[loc + 16 :]
                            log.debug("Found and replaced IP %s at location %08x" % (extraip.decode( ), loc))
                            if len(file) != origsize :
                                raise Exception("SIZE MISMATCH")

                for ip in globalvars.ip_addresses :

                    loc = file.find(ip)
                    if loc != -1 :
                        if config["public_ip"] != "0.0.0.0" :
                            server_ip = config["public_ip"]
                            server_ip = server_ip.encode( )
                            replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
                            file = file[:loc] + replace_ip + file[loc + 16 :]
                            log.debug(filename + ": Found and replaced IP %16s at location %08x" % (ip, loc))
                            if len(file) != origsize :
                                raise Exception("SIZE MISMATCH")
                        else :

                            replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
                            file = file[:loc] + replace_ip + file[loc + 16 :]
                            log.debug(filename + ": Found and replaced IP %16s at location %08x" % (ip, loc))
                            if len(file) != origsize :
                                raise Exception("SIZE MISMATCH")

                if not config["server_ip"] == "127.0.0.1" :
                    for ip in globalvars.loopback_ips :
                        loc = file.find(ip)
                        if loc != -1 :
                            if config["public_ip"] != "0.0.0.0" :
                                server_ip = config["public_ip"]
                                server_ip = server_ip.encode( )
                                replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
                                file = file[:loc] + replace_ip + file[loc + 16 :]
                                log.debug(filename + ": Found and replaced IP %16s at location %08x" % (ip, loc))
                            else :
                                replace_ip = server_ip + (b"\x00" * (16 - len(server_ip)))
                                file = file[:loc] + replace_ip + file[loc + 16 :]
                                log.debug(filename + ": Found and replaced IP %16s at location %08x" % (ip, loc))

                if config["public_ip"] != "0.0.0.0" :
                    if not config["http_port"] == "steam" :

                        for (search, replace, info) in globalvars.replace_string_name_space(False) :
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                log.debug("WARNING: Cannot replace " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ) + " as it's too long")
                            elif missinglength == 0 :
                                file = file.replace(search, replace)
                                log.debug("Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")

                            else :
                                file = file.replace(search, replace + (b'\x20' * missinglength))
                                log.debug("Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                        for (search, replace, info) in globalvars.replace_string_name(False) :
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                log.debug("WARNING: Cannot replace " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ) + " as it's too long")
                            elif missinglength == 0 :
                                file = file.replace(search, replace)
                                log.debug("Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                            else :
                                file = file.replace(search, replace + (b'\x00' * missinglength))
                                log.debug("Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                else :
                    if not config["http_port"] == "steam" :
                        for (search, replace, info) in globalvars.replace_string_name_space(True) :
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                log.debug("WARNING: Cannot replace " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ) + " as it's too long")
                            elif missinglength == 0 :
                                file = file.replace(search, replace)
                                log.debug("Replaced " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ))
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                            else :
                                file = file.replace(search, replace + (b'\x20' * missinglength))
                                log.debug("Replaced " + info.decode( ))  # + " " + search + " with " + replace)
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                        for (search, replace, info) in globalvars.replace_string_name(True) :
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                log.debug("WARNING: Cannot replace " + info.decode( ) + " " + search.decode( ) + " with " + replace.decode( ) + " as it's too long")
                            elif missinglength == 0 :
                                file = file.replace(search, replace)
                                log.debug("Replaced " + info.decode( ))  # + " " + search + " with " + replace)
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")
                            else :
                                file = file.replace(search, replace + (b'\x00' * missinglength))
                                log.debug("Replaced " + info.decode( ))  # + " " + search + " with " + replace)"""
                                if len(file) != origsize :
                                    raise Exception("SIZE MISMATCH")

                time.sleep(1)
                h = open("files/temp/" + dirname + ".neutered.gcf", "wb")
                h.write(file)
                h.close( )
                time.sleep(1)
                log.info("Converting fixed gcf to cache...")
                gcf2storage("files/temp/" + dirname + ".neutered.gcf")
                time.sleep(1)
                os.remove("files/temp/" + dirname + ".neutered.gcf")
                log.debug("****************************************")