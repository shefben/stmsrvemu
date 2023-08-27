import threading, logging, struct, binascii, os.path, zlib, os, shutil, atexit, ast
import utilities
import blob_utilities
import storage_utilities
import encryption
import config
import globalvars
import emu_socket
import time
import steamemu.logger

from Crypto.Hash import SHA
from Steam2.manifest import *
from Steam2.neuter import neuter
from Steam2.manifest2 import Manifest2
from Steam2.checksum2 import Checksum2
from Steam2.checksum3 import Checksum3
from gcf_to_storage import gcf2storage
from time import sleep
from Crypto.Hash import SHA
from contentserverlist_utilities import send_removal, send_heartbeat
from networkhandler import TCPNetworkHandler

log = logging.getLogger("ContentSRV")
app_list = []
csConnectionCount = 0


class contentserver(TCPNetworkHandler):
    global log
    
    def check_thread_status(self):
        while True:
            if self.thread2.is_alive():
                log.error("[content server] Thread is alive")
            else:
                log.error("[content server] Thread has died... attempting restart")
                self.thread2.start()
                break
        time.sleep(45 * 60)  # Delay for 45 minutes

    def __init__(self, port, config):
        super(contentserver, self).__init__(config, port)  # Create an instance of NetworkHandler
        self.contentserver_info = {
            'ip_address': globalvars.serverip,
            'port': int(self.port),
            'region': globalvars.cs_region,
            'timestamp': 1623276000
        }
        
        self.applist = self.parse_manifest_files(self.contentserver_info)
    
        self.thread2 = threading.Thread(target=self.heartbeat_thread)
        self.thread2.daemon = True
        self.thread2.start()
        
        #thread_status_checker = threading.Thread(target=self.check_thread_status)
        #thread_status_checker.daemon = True
        #thread_status_checker.start()
    
    def heartbeat_thread(self):       
        while True:
            send_heartbeat(self.contentserver_info, self.applist)
            time.sleep(1800) # 30 minutes
            
    def handle_client(self, clientsocket, address):
        global csConnectionCount
        csConnectionCount += 1
        clientid = str(address) + ": "
        log.info(clientid + "Connected to Content Server")

        msg = clientsocket.recv(4)

        if len(msg) == 0 :
            log.info(clientid + "Got simple handshake. Closing connection.")
        elif msg == "\x00\x00\x00\x02" or msg == "\x00\x00\x00\x03" : #x02 for 2012
            log.info(clientid + "Package mode entered")
            clientsocket.send("\x01")
            while True :
                msg = clientsocket.recv_withlen()

                if not msg :
                    log.info(clientid + "no message received")
                    break

                command = struct.unpack(">L", msg[:4])[0]

                if command == 2 :
                    cellid = "\x00\x00" + struct.pack('<h', int(self.config["cellid"]) )
                    clientsocket.send(cellid)  #cellid
                    break

                elif command == 3 :
                    log.info(clientid + "Exiting package mode")
                    break

                elif command == 0 :
                    (dummy1, filenamelength) = struct.unpack(">LL", msg[4:12])
                    filename = msg[12:12+filenamelength]
                    dummy2 = struct.unpack(">L", msg[12+filenamelength:])[0]

                    if len(msg) != (filenamelength + 16) :
                        log.warning(clientid + "There is extra data in the request")

                    log.info(clientid + filename)

                    if filename[-14:] == "_rsa_signature" :
                        newfilename = filename[:-14]
                        if self.config["public_ip"] != "0.0.0.0" :
                            try :
                                os.mkdir("files/cache/external")
                            except OSError as error :
                                log.debug(clientid + "External pkg dir already exists")
                            
                            try :
                                os.mkdir("files/cache/internal")
                            except OSError as error :
                                log.debug(clientid + "Internal pkg dir already exists")
                            
                            if clientid.startswith(globalvars.servernet) :
                                if not os.path.isfile("files/cache/internal/" + newfilename) :
                                    neuter(self.config["packagedir"] + newfilename, "files/cache/internal/" + newfilename, self.config["server_ip"], self.config["dir_server_port"])
                                f = open('files/cache/internal/' + newfilename, 'rb')
                            else :
                                if not os.path.isfile("files/cache/external/" + newfilename) :
                                    neuter(self.config["packagedir"] + newfilename, "files/cache/external/" + newfilename, self.config["public_ip"], self.config["dir_server_port"])
                                f = open('files/cache/external/' + newfilename, 'rb')
                        else :
                            if not os.path.isfile("files/cache/" + newfilename) :
                                neuter(self.config["packagedir"] + newfilename, "files/cache/" + newfilename, self.config["server_ip"], self.config["dir_server_port"])
                            f = open('files/cache/' + newfilename, 'rb')

                        file = f.read()
                        f.close()

                        signature = encryption.rsa_sign_message(encryption.network_key_sign, file)

                        reply = struct.pack('>LL', len(signature), len(signature)) + signature

                        clientsocket.send(reply)

                    else :
                        if self.config["public_ip"] != "0.0.0.0" :
                            try :
                                os.mkdir("files/cache/external")
                            except OSError as error :
                                log.debug(clientid + "External pkg dir already exists")
                            
                            try :
                                os.mkdir("files/cache/internal")
                            except OSError as error :
                                log.debug(clientid + "Internal pkg dir already exists")
                            
                            if clientid.startswith(globalvars.servernet) :
                                if not os.path.isfile("files/cache/internal/" + filename) :
                                    neuter(self.config["packagedir"] + filename, "files/cache/internal/" + filename, self.config["server_ip"], self.config["dir_server_port"])
                                f = open('files/cache/internal/' + filename, 'rb')
                            else :
                                if not os.path.isfile("files/cache/external/" + filename) :
                                    neuter(self.config["packagedir"] + filename, "files/cache/external/" + filename, self.config["public_ip"], self.config["dir_server_port"])
                                f = open('files/cache/external/' + filename, 'rb')
                        else :
                            if not os.path.isfile("files/cache/" + filename) :
                                neuter(self.config["packagedir"] + filename, "files/cache/" + filename, self.config["server_ip"], self.config["dir_server_port"])
                            f = open('files/cache/' + filename, 'rb')
                            
                        file = f.read()
                        f.close()

                        reply = struct.pack('>LL', len(file), len(file))

                        clientsocket.send( reply )
                        clientsocket.send(file, False)

                else :
                    log.warning(clientid +"invalid Command")

        elif msg == "\x00\x00\x00\x07" :

            log.info(clientid + "Storage mode entered")

            storagesopen = 0
            storages = {}

            clientsocket.send("\x01") # this should just be the handshake

            while True :

                command = clientsocket.recv_withlen()

                if command[0] == "\x00" :

                    if len(command) == 10 :
                        clientsocket.send("\x01")
                        break
                    elif len(command) > 1 :
                        log.info("Banner message: " + binascii.b2a_hex(command))
                        
                        url = "http://" + self.config["http_ip"] + self.config["http_port"] + self.config["banner_url"]

                        reply = struct.pack(">cH", "\x01", len(url)) + url

                        clientsocket.send(reply)
                    else :
                        clientsocket.send("")
                        
                elif command[0] == "\x02" :

                    if os.path.isfile("files/cache/secondblob.bin") :
                        f = open("files/cache/secondblob.bin", "rb")
                        blob = f.read()
                        f.close()
                    elif os.path.isfile("files/secondblob.py") :
                        if not os.path.isfile("files/secondblob.py.orig") :
                            shutil.copy2("files/secondblob.py","files/secondblob.py.orig")
                        g = open("files/secondblob.py", "r")
                        file = g.read()
                        g.close()
                    
                        for (search, replace, info) in globalvars.replacestringsCDR :
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                print("WARNING: Replacement text " + replace + " is too long! Not replaced!")
                            else :
                                fileold = file
                                file = file.replace(search, replace)
                                if (search in fileold) and (replace in file) :
                                    print("Replaced " + info + " " + search + " with " + replace)
                        h = open("files/secondblob.py", "w")
                        h.write(file)
                        h.close()
                        
                        execdict = {}
                        execdict_temp_01 = {}
                        execdict_temp_02 = {}
                        execfile("files/secondblob.py", execdict)
                        
                        if os.path.isfile("files/extrablob.py") :
                            execdict_update = {}
                            with open("files/extrablob.py", 'r') as m :
                                userblobstr_upd = m.read()
                            execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])
                            for k in execdict_update :
                                for j in execdict["blob"] :
                                    if j == k :
                                        execdict["blob"][j].update(execdict_update[k])
                                    else :
                                        if k == "\x01\x00\x00\x00" :
                                            execdict_temp_01.update(execdict_update[k])
                                        elif k == "\x02\x00\x00\x00" :
                                            execdict_temp_02.update(execdict_update[k])

                            for k,v in execdict_temp_01.items() :
                                execdict["blob"].pop(k,v)

                            for k,v in execdict_temp_02.items() :
                                execdict["blob"].pop(k,v)
                            
                        blob = blob_utilities.blob_serialize(execdict["blob"])
                    
                        if blob[0:2] == "\x01\x43" :
                            blob = zlib.decompress(blob[20:])
                        
                        start_search = 0
                        while True :
                            found = blob.find("\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
                            if found < 0 :
                                break

                            #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                            BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                            foundstring = blob[found:found + 160]
                            blob = blob.replace(foundstring, BERstring)
                            start_search = found + 160
    
                        compressed_blob = zlib.compress(blob, 9)
                        blob = "\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob
                    
                        cache_option = self.config["use_cached_blob"]
                        if cache_option == "true" :
                            f = open("files/cache/secondblob.bin", "wb")
                            f.write(blob)
                            f.close()
                    
                    else :
                        if not os.path.isfile("files/secondblob.bin.orig") :
                            shutil.copy2("files/secondblob.bin","files/secondblob.bin.orig")
                        f = open("files/secondblob.bin", "rb")
                        blob = f.read()
                        f.close()
                    
                        if blob[0:2] == "\x01\x43":
                            blob = zlib.decompress(blob[20:])
                        blob2 = blob_utilities.blob_unserialize(blob)
                        blob3 = blob_utilities.blob_dump(blob2)
                        file = "blob = " + blob3
                    
                        for (search, replace, info) in globalvars.replacestringsCDR :
                            print("Fixing CDR")
                            fulllength = len(search)
                            newlength = len(replace)
                            missinglength = fulllength - newlength
                            if missinglength < 0 :
                                print("WARNING: Replacement text " + replace + " is too long! Not replaced!")
                            else :
                                file = file.replace(search, replace)
                                print("Replaced " + info + " " + search + " with " + replace)
                    
                        execdict = {}
                        execdict_temp_01 = {}
                        execdict_temp_02 = {}
                        exec(file, execdict)
                        
                        if os.path.isfile("files/extrablob.py") :
                            execdict_update = {}
                            with open("files/extrablob.py", 'r') as m :
                                userblobstr_upd = m.read()
                            execdict_update = ast.literal_eval(userblobstr_upd[7:len(userblobstr_upd)])
                            for k in execdict_update :
                                for j in execdict["blob"] :
                                    if j == k :
                                        execdict["blob"][j].update(execdict_update[k])
                                    else :
                                        if k == "\x01\x00\x00\x00" :
                                            execdict_temp_01.update(execdict_update[k])
                                        elif k == "\x02\x00\x00\x00" :
                                            execdict_temp_02.update(execdict_update[k])

                            for k,v in execdict_temp_01.items() :
                                execdict["blob"].pop(k,v)

                            for k,v in execdict_temp_02.items() :
                                execdict["blob"].pop(k,v)
                                        
                        blob = blob_utilities.blob_serialize(execdict["blob"])
                    
                        h = open("files/secondblob.bin", "wb")
                        h.write(blob)
                        h.close()
                    
                        g = open("files/secondblob.bin", "rb")
                        blob = g.read()
                        g.close()
                    
                        if blob[0:2] == "\x01\x43" :
                            blob = zlib.decompress(blob[20:])
                        
                        start_search = 0
                        while True :
                            found = blob.find("\x30\x81\x9d\x30\x0d\x06\x09\x2a", start_search)
                            if found < 0 :
                                break

                            #BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex("bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059") + "\x02\x01\x11"
                            BERstring = binascii.a2b_hex("30819d300d06092a864886f70d010101050003818b0030818702818100") + binascii.a2b_hex(self.config["net_key_n"][2:]) + "\x02\x01\x11"
                            foundstring = blob[found:found + 160]
                            blob = blob.replace(foundstring, BERstring)
                            start_search = found + 160

                        compressed_blob = zlib.compress(blob, 9)
                        blob = "\x01\x43" + struct.pack("<QQH", len(compressed_blob) + 20, len(blob), 9) + compressed_blob
                    
                        cache_option = self.config["use_cached_blob"]
                        if cache_option == "true" :
                            f = open("files/cache/secondblob.bin", "wb")
                            f.write(blob)
                            f.close()

                    checksum = SHA.new(blob).digest()

                    if checksum == command[1:] :
                        log.info(clientid + "Client has matching checksum for secondblob")
                        log.debug(clientid + "We validate it: " + binascii.b2a_hex(command))

                        clientsocket.send("\x00\x00\x00\x00")

                    else :
                        log.info(clientid + "Client didn't match our checksum for secondblob")
                        log.debug(clientid + "Sending new blob: " + binascii.b2a_hex(command))

                        clientsocket.send_withlen(blob, False)

                elif command[0] == "\x09" or command[0] == "\x0a" : #09 is used by early clients without a ticket

                    if command[0] == "\x0a" :
                        log.info(clientid + "Login packet used")
                    #else :
                        #log.error(clientid + "Not logged in")

                        #reply = struct.pack(">LLc", connid, messageid, "\x01")
                        #clientsocket.send(reply)

                        #break

                    (connid, messageid, app, version) = struct.unpack(">xLLLL", command[0:17])

                    log.info(clientid + "Opening application %d %d" % (app, version))
                    connid = pow(2,31) + connid

                    try :
                        s = storage_utilities.Storage(str(app), self.config["storagedir"], str(version))
                    except Exception :
                        log.error("Application not installed! %d %d" % (app, version))

                        reply = struct.pack(">LLc", connid, messageid, "\x01")
                        clientsocket.send(reply)

                        break

                    storageid = storagesopen
                    storagesopen = storagesopen + 1

                    storages[storageid] = s
                    storages[storageid].app = app
                    storages[storageid].version = version
                    
                    if str(app) == "3" or str(app) == "7" :
                        if not os.path.isfile("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(version) + ".manifest") :
                            if os.path.isfile("files/convert/" + str(app) + "_" + str(version) + ".gcf") :
                                log.info("Fixing files in app " + str(app) + " version " + str(version))
                                g = open("files/convert/" + str(app) + "_" + str(version) + ".gcf", "rb")
                                file = g.read()
                                g.close()
                                for (search, replace, info) in globalvars.replacestrings :
                                    fulllength = len(search)
                                    newlength = len(replace)
                                    missinglength = fulllength - newlength
                                    if missinglength < 0 :
                                        print("WARNING: Replacement text " + replace + " is too long! Not replaced!")
                                    elif missinglength == 0 :
                                        file = file.replace(search, replace)
                                        print("Replaced", info)
                                    else :
                                        file = file.replace(search, replace + ('\x00' * missinglength))
                                        print("Replaced", info)

                                h = open("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf", "wb")
                                h.write(file)
                                h.close()
                                gcf2storage("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")
                                sleep(1)
                                os.remove("files/temp/" + str(app) + "_" + str(version) + ".neutered.gcf")
                    
                    if os.path.isfile("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(version) + ".manifest") :
                        f = open("files/cache/" + str(app) + "_" + str(version) + "/" + str(app) + "_" + str(version) + ".manifest", "rb")
                        log.info(clientid + str(app) + "_" + str(version) + " is a cached depot")
                    elif os.path.isfile(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest") :
                        f = open(self.config["v2manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
                        log.info(clientid + str(app) + "_" + str(version) + " is a v0.2 depot")
                    elif os.path.isfile(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest") :
                        f = open(self.config["manifestdir"] + str(app) + "_" + str(version) + ".manifest", "rb")
                        log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 depot")
                    elif os.path.isdir(self.config["v3manifestdir2"]) :
                        if os.path.isfile(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest") :
                            f = open(self.config["v3manifestdir2"] + str(app) + "_" + str(version) + ".manifest", "rb")
                            log.info(clientid + str(app) + "_" + str(version) + " is a v0.3 extra depot")
                        else :
                            log.error("Manifest not found for %s %s " % (app, version))
                            reply = struct.pack(">LLc", connid, messageid, "\x01")
                            clientsocket.send(reply)
                            break
                    else :
                        log.error("Manifest not found for %s %s " % (app, version))
                        reply = struct.pack(">LLc", connid, messageid, "\x01")
                        clientsocket.send(reply)
                        break
                    manifest = f.read()
                    f.close()
                    
                    manifest_appid = struct.unpack('<L', manifest[4:8])[0]
                    manifest_verid = struct.unpack('<L', manifest[8:12])[0]
                    log.debug(clientid + ("Manifest ID: %s Version: %s" % (manifest_appid, manifest_verid)))
                    if (int(manifest_appid) != int(app)) or (int(manifest_verid) != int(version)) :
                        log.error("Manifest doesn't match requested file: (%s, %s) (%s, %s)" % (app, version, manifest_appid, manifest_verid))

                        reply = struct.pack(">LLc", connid, messageid, "\x01")
                        clientsocket.send(reply)

                        break
                    
                    globalvars.converting = "0"

                    fingerprint = manifest[0x30:0x34]
                    oldchecksum = manifest[0x34:0x38]
                    manifest = manifest[:0x30] + "\x00" * 8 + manifest[0x38:]
                    checksum = struct.pack("<i", zlib.adler32(manifest, 0))
                    manifest = manifest[:0x30] + fingerprint + checksum + manifest[0x38:]
                    
                    log.debug("Checksum fixed from " + binascii.b2a_hex(oldchecksum) + " to " + binascii.b2a_hex(checksum))
                    
                    storages[storageid].manifest = manifest

                    checksum = struct.unpack("<L", manifest[0x30:0x34])[0] # FIXED, possible bug source

                    reply = struct.pack(">LLcLL", connid, messageid, "\x00", storageid, checksum)

                    clientsocket.send(reply)

                elif command[0] == "\x01" :

                    clientsocket.send("")
                    break

                elif command[0] == "\x03" :

                    (storageid, messageid) = struct.unpack(">xLL", command)

                    del storages[storageid]

                    reply = struct.pack(">LLc", storageid, messageid, "\x00")

                    log.info(clientid + "Closing down storage %d" % storageid)

                    clientsocket.send(reply)

                elif command[0] == "\x04" :

                    log.info(clientid + "Sending manifest")

                    (storageid, messageid) = struct.unpack(">xLL", command)

                    manifest = storages[storageid].manifest

                    reply = struct.pack(">LLcL", storageid, messageid, "\x00", len(manifest))

                    clientsocket.send(reply)

                    reply = struct.pack(">LLL", storageid, messageid, len(manifest))

                    clientsocket.send(reply + manifest, False)

                elif command[0] == "\x05" :
                    log.info(clientid + "Sending app update information")
                    (storageid, messageid, oldversion) = struct.unpack(">xLLL", command)
                    appid = storages[storageid].app
                    version = storages[storageid].version
                    log.info("Old GCF version: " + str(appid) + "_" + str(oldversion))
                    log.info("New GCF version: " + str(appid) + "_" + str(version))
                    manifestNew = Manifest2(appid, version)
                    manifestOld = Manifest2(appid, oldversion)

                    if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(version) + ".manifest") :
                        checksumNew = Checksum3(appid)
                    else :
                        checksumNew = Checksum2(appid, version)

                    if os.path.isfile(self.config["v2manifestdir"] + str(appid) + "_" + str(oldversion) + ".manifest") :
                        checksumOld = Checksum3(appid)
                    else :
                        checksumOld = Checksum2(appid, version)

                    filesOld = {}
                    filesNew = {}
                    for n in manifestOld.nodes.values():
                        if n.fileId != 0xffffffff:
                            n.checksum = checksumOld.getchecksums_raw(n.fileId)
                            filesOld[n.fullFilename] = n

                    for n in manifestNew.nodes.values():
                        if n.fileId != 0xffffffff:
                            n.checksum = checksumNew.getchecksums_raw(n.fileId)
                            filesNew[n.fullFilename] = n
                       
                    del manifestNew
                    del manifestOld

                    changedFiles = []

                    for filename in filesOld:
                        if filename in filesNew and filesOld[filename].checksum != filesNew[filename].checksum:
                            changedFiles.append(filesOld[filename].fileId)
                            log.debug("Changed file: " + str(filename) + " : " + str(filesOld[filename].fileId))
                        if not filename in filesNew:
                            changedFiles.append(filesOld[filename].fileId)
                            #if not 0xffffffff in changedFiles:
                                #changedFiles.append(0xffffffff)                            
                            log.debug("Deleted file: " + str(filename) + " : " + str(filesOld[filename].fileId))
                            
                    for x in range(len(changedFiles)):
                        log.debug(changedFiles[x],)
                    
                    count = len(changedFiles)
                    log.info("Number of changed files: " + str(count))

                    if count == 0:
                        reply = struct.pack(">LLcL", storageid, messageid, "\x01", 0)
                        clientsocket.send(reply)
                    else:
                        reply = struct.pack(">LLcL", storageid, messageid, "\x02", count)
                        clientsocket.send(reply)
                        
                        changedFilesTmp = []
                        for fileid in changedFiles:
                            changedFilesTmp.append(struct.pack("<L", fileid))
                        updatefiles = "".join(changedFilesTmp)
                        
                        reply = struct.pack(">LL", storageid, messageid)
                        clientsocket.send(reply)
                        clientsocket.send_withlen(updatefiles)
                    
                elif command[0] == "\x06" :

                    log.info(clientid + "Sending checksums")

                    (storageid, messageid) = struct.unpack(">xLL", command)

                    if os.path.isfile("files/cache/" + str(storages[storageid].app) + "_" + str(storages[storageid].version) + "/" + str(storages[storageid].app) + "_" + str(storages[storageid].version) + ".manifest") :
                        filename = "files/cache/" + str(storages[storageid].app) + "_" + str(storages[storageid].version) + "/"  + str(storages[storageid].app) + ".checksums"
                    elif os.path.isfile(self.config["v2manifestdir"] + str(storages[storageid].app) + "_" + str(storages[storageid].version) + ".manifest") :
                        filename = self.config["v2storagedir"] + str(storages[storageid].app) + ".checksums"
                    elif os.path.isfile(self.config["manifestdir"] + str(storages[storageid].app) + "_" + str(storages[storageid].version) + ".manifest") :
                        filename = self.config["storagedir"] + str(storages[storageid].app) + ".checksums"
                    elif os.path.isdir(self.config["v3manifestdir2"]) :
                        if os.path.isfile(self.config["v3manifestdir2"] + str(storages[storageid].app) + "_" + str(storages[storageid].version) + ".manifest") :
                            filename = self.config["v3storagedir2"] + str(storages[storageid].app) + ".checksums"
                        else :
                            log.error("Manifest not found for %s %s " % (app, version))
                            reply = struct.pack(">LLc", connid, messageid, "\x01")
                            clientsocket.send(reply)
                            break
                    else :
                        log.error("Checksums not found for %s %s " % (app, version))
                        reply = struct.pack(">LLc", connid, messageid, "\x01")
                        clientsocket.send(reply)
                        break
                    f = open(filename, "rb")
                    file = f.read()
                    f.close()

                    # hack to rip out old sig, insert new
                    file = file[0:-128]
                    signature = encryption.rsa_sign_message(encryption.network_key_sign, file)

                    file = file + signature

                    reply = struct.pack(">LLcL", storageid, messageid, "\x00", len(file))

                    clientsocket.send(reply)

                    reply = struct.pack(">LLL", storageid, messageid, len(file))

                    clientsocket.send(reply + file, False)

                elif command[0] == "\x07" :

                    (storageid, messageid, fileid, filepart, numparts, priority) = struct.unpack(">xLLLLLB", command)

                    (chunks, filemode) = storages[storageid].readchunks(fileid, filepart, numparts)

                    reply = struct.pack(">LLcLL", storageid, messageid, "\x00", len(chunks), filemode)

                    clientsocket.send(reply)

                    for chunk in chunks :

                        reply = struct.pack(">LLL", storageid, messageid, len(chunk))

                        clientsocket.send(reply)

                        reply = struct.pack(">LLL", storageid, messageid, len(chunk))

                        clientsocket.send(reply)

                        clientsocket.send(chunk, False)

                elif command[0] == "\x08" :

                    log.warning("08 - Invalid Command!")
                    clientsocket.send("\x01")

                else :

                    log.warning(binascii.b2a_hex(command[0]) + " - Invalid Command!")
                    clientsocket.send("\x01")

                    break
        elif msg == "\x03\x00\x00\x00" :
            log.info(clientid + "Unknown mode entered")
            clientsocket.send("\x00")
        else :
            log.warning("Invalid Command: " + binascii.b2a_hex(msg))

        clientsocket.close()
        log.info(clientid + "Disconnected from Content Server")

    def parse_manifest_files(self, contentserver_info):
        global app_list
        # Define the locations to search for '.manifest' files
        locations = ['files/cache/', self.config["v2manifestdir"], self.config["manifestdir"]]
        app_buffer = ""
        for location in locations:
            for file_name in os.listdir(location):
                if file_name.endswith('.manifest'):
                    # Extract app ID and version from the file name
                    app_id, version = file_name.split('_')
                    version = version.rstrip('.manifest')
                    #for appid, version in self.applist:
                    #print("appid:", app_id)
                    #print("version:", version)
                    # Append app ID and version to app_list in this format
                    app_buffer += str(app_id) + "\x00" + str(version) + "\x00\x00"
                    app_list.append((app_id, version))
        return app_buffer
