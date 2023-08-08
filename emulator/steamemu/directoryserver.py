import datetime
import threading, logging, struct, binascii, time, datetime, atexit
import time
import utilities
import emu_socket
import globalvars
import steamemu.logger
import socket as pysocket
import serverlist_utilities
from serverlist_utilities import unpack_server_info, DirServerManager
from networkhandler import TCPNetworkHandler
log = logging.getLogger("DirectorySRV")

manager = DirServerManager()    
dirConnectionCount = 0

incoming_rate = 0
outgoing_rate = 0

class directoryserver(TCPNetworkHandler):
    global manager
    global log
    
    def __init__(self, port, config):
        server_type = "" if globalvars.dir_ismaster == 1 else "dirserver"
        super(directoryserver, self).__init__(config, int(port), server_type)

        self.server_type = "masterdirserver" if globalvars.dir_ismaster == 1 else "dirserver"
        self.server_info = {
            'ip_address': globalvars.serverip,
            'port': int(self.port),
            'server_type': self.server_type,
            'timestamp': int(time.time())
        }
        log = logging.getLogger("DirectorySRV")
        # atexit.register(remove_from_dir(globalvars.serverip, int(self.port), self.server_type)) # add function for cleanup when program exits
        if globalvars.dir_ismaster == 1 :  # add ourself to the serverlist as a directoryserver type, with a 0'd timestamp to indicate that it cannot be removed 
            manager.add_server_info(globalvars.serverip, self.config["dir_server_port"], self.server_type, 1)
        #    log = logging.getLogger("master_dirserver")
        else:       
            log.info("Connecting to Master Directory Server")

            
        thread = threading.Thread(target=self.expired_servers_thread) # Thread for removing servers older than 1 hour
        thread.daemon = True
        thread.start()
        # atexit.register(remove_from_dir(globalvars.serverip, int(self.port), self.server_type)) # add function for cleanup when program exits

        manager.add_server_info(globalvars.serverip, self.config["dir_server_port"], self.server_type, 1)

        if globalvars.dir_ismaster != 1 :  # add ourself to the serverlist as a directoryserver type, with a 0'd timestamp to indicate that it cannot be removed       
            log.info("Connecting to Master Directory Server")
            
            recieved_list = send_listrequest() #since we are a slave, get the full current list from the master
            index = 0
            while index < len(recieved_list):
                ip_address = recieved_list[index]
                port = recieved_list[index + 1]
                server_type = recieved_list[index + 2]
                timestamp = recieved_list[index + 3]
                manager.add_server_info([ip_address, int(port), server_type, timestamp])
				
		datarate_thread = threading.Thread(target=self.netstats)
	        datarate_thread.daemon = True
	        datarate_thread.start()    
        else:
            self.slavedir_list = []
            
    def netstats(self):
        while True:
            incoming_rate, outgoing_rate = self.calculate_data_rates()
            time.sleep(0.5)
            print(incoming_rate)
    
    def handle_client(self, clientsocket, address):
        global server_list
        global dirConnectionCount
        global log
        #threading.Thread.__init__(self)

        
        clientid = str(address) + ": "
        if globalvars.dir_ismaster == 1:           
            log.info(clientid + "Connected to Directory Server")
        else:           
            log.info(clientid + "Connected to Slave/Peer Directory Server")
               
        msg = clientsocket.recv(4)
        log.debug(binascii.b2a_hex(msg))

        if msg == "\x05\xaa\x6c\x15": #slave to master serverlist request
            list_size, masterlist = manager.pack_serverlist()
            packed_length = struct.unpack('!I',  list_size[:4])[0]
            clientsocket.send(packed_length) # handshake confirmed  
            
            size_response = clientsocket.recv(1)
            
            if size_response == '\x01':
                clientsocket.send(masterlist)
                
                slave_response = clientsocket.recv(1)
                
                if slave_response == '\x01':
                    clientsocket.close()

        elif msg == "\x00\x3e\x7b\x11" :            
            clientsocket.send("\x01") # handshake confirmed
            msg = clientsocket.recv(1024)
            command = msg[0]           
            log.debug(binascii.b2a_hex(command))
            
            if command == "\x1a": # Add server entry to the list             
                ip_address, port, server_type, timestamp = unpack_server_info(msg)
                try:
                    pysocket.inet_aton(ip_address)
                except pysocket.error:
                    log.warning(clientid + " Sent bad heartbeat packet: " + binascii.b2a_hex(msg))
                    clientsocket.send("\x00") # message decryption failed, the only response we give for failure
                    clientsocket.close()
                    log.info(clientid + "Disconnected from Directory Server")
                    return
                       
                manager.add_server_info(ip_address, int(port), server_type)
                
                clientsocket.send("\x01")
                log.info("[" + server_type + "] " + clientid + "Added to Directory Server")
                
                log.debug("IP Address: " + ip_address)
                log.debug("Port: " + str(port))
                log.debug("Server Type: " + server_type)
                log.debug("Timestamp: " + datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S'))
                
                if server_type == "dirserver" and globalvars.dir_ismaster == 1: # only add to the slave list if you are master
                    self.slavedir_list.append([ip_address, int(port)])
                    
                if globalvars.dir_ismaster != 1: # relay any requests to the master server aswell
                    clientsocket.sendto(msg, str(config["masterdir_ipport"]))
                else: # relay anything from the master to all of the slaves..
                    if len(self.slavedir_list) != 0:
                        for entry in self.slavedir_list:
                            if enctry[0] != ip_address and int(entry[1]) != int(port): #make sure we arent sending the slave server its own heartbeat...
                                forward_heartbeat(ip_address, port, msg)
                
            elif command == "\x1d": # Remove server entry from the list
                ip_address, port, server_type = unpack_removal_info(msg)
                try:
                    pysocket.inet_aton(ip_address)
                except pysocket.error:
                    log.warning(clientid + " Sent bad removal request packet: " + binascii.b2a_hex(msg))
                    clientsocket.send("\x00") # message decryption failed, the only response we give for failure
                    clientsocket.close()
                    log.info(clientid + "Disconnected from Directory Server")
                    return
                                
                if manager.remove_entry(ip, port, server_type) is True:
                    clientsocket.send("\x01")
                    log.info("[" + server_type + "] " + clientid + "Removed server from Directory Server")
                    if globalvars.dir_ismaster != 1: # relay any requests to the master server aswell
                        clientsocket.sendto(msg, str(config["masterdir_ipport"]))
                else: # couldnt remove server because: doesnt exists, problem with list
                    clientsocket.send("\x01")
                    log.info("[" + server_type + "] " + clientid + "There was an issue removing the server from Directory Server")  
                    
            # BEN TODO: Add packet for slave/peer dir servers to recieve master dir serverlist
                    
        elif msg == "\x00\x00\x00\x01" or msg == "\x00\x00\x00\x02":
            dirConnectionCount += 1 # only count user's, ignore heartbeat/other servers
            clientsocket.send("\x01")
            msg = clientsocket.recv_withlen()
            command = msg[0]
            log.debug(binascii.b2a_hex(command))
            reply = "\x00\x00"
            if command == "\x00" or command == "\x12" or command == "\x1a": # Send out list of authservers
                log.info(clientid + "Sending out list of Auth Servers: " + binascii.b2a_hex(command))    
                reply = manager.get_and_prep_server_list("authserver")
            elif command == "\x03": # Send out list of Configuration Servers
                log.info(clientid + "Sending out list of Configuration Servers")
                reply = manager.get_and_prep_server_list("configserver")
            elif command == "\x06" or command == "\x05" : # send out content list servers
                log.info(clientid + "Sending out list of Content Server Directory Servers")
                reply = manager.get_and_prep_server_list("csdserver")
            elif command == "\x0f" : # hl master server
                log.info(clientid + "Sending out list of HL Master Servers")
                reply = manager.get_and_prep_server_list("masterhlserver")
            elif command == "\x14" : # send out CSER server (not implemented)
                log.info(clientid + "Sending out list of CSER Servers")
                reply = manager.get_and_prep_server_list("cserserver")
            elif command == "\x18" or command == "\x1e": # source master server & ragdoll kungfu use the same exact protocol
                log.info(clientid + "Requesting Source Master Servers")
                reply = manager.get_and_prep_server_list("masterhl2server")
            elif command == "\x0A" : # remote file harvest master server
                log.info(clientid + "Sending out list of Remote File Harvest Master Servers")
                reply = manager.get_and_prep_server_list("harvestserver")
            elif command == "\x12" : #userid ticket validation server address, not supported yet
                log.info(clientid + "Sending out list of Client / Account Authentication Servers")
                reply = manager.get_and_prep_server_list("validationserver")
            elif command == "\x0B" or command == "\x1c" : #  master VCDS Validation (New valve cdkey Authentication) server
                log.info(clientid + "Sending out list of VCDS Validation (New valve CDKey Authentication) Master Servers")
                reply = manager.get_and_prep_server_list("validationserver")
            elif command == "\x07" : # Ticket Validation master server
                log.info(clientid + "Sending out list of Ticket Validation Master Servers")
                reply = manager.get_and_prep_server_list("validationserver")
            elif command == "\x10" : #  Friends master server
                log.info(clientid + "Sending out list of Messaging Servers")
                reply = manager.get_and_prep_server_list("messagingserver")
            elif command == "\x0D" or command == "\x0E" : # all MCS Master Public Content master server
                log.info(clientid + "Sending out list of MCS Master Public Content Master Servers")
                reply = manager.get_and_prep_server_list("csdserver") 
            elif command == "\x1c" :
                  
                if binascii.b2a_hex(msg) == "1c600f2d40" : 
                    log.info(clientid + "Sending out CSDS and 2 Authentication Servers")
                    csds_servers = manager.get_and_prep_server_list("csdserver")
                    auth_servers = manager.get_and_prep_server_list("authserver")
                    reply = struct.pack(">H", 3)  # Total number of servers in the reply
                    
                    if csds_servers :
                        reply += utilities.encodeIP((csds_servers[0].ip, csds_servers[0].port))
                    else :
                        reply = "\x00\x00"

                    if len(auth_servers) > 0 :
                        if len(auth_servers) >= 2 :
                            reply += utilities.encodeIP((auth_servers[0].ip, auth_servers[0].port))
                            reply += utilities.encodeIP((auth_servers[1].ip, auth_servers[1].port))
                        else:
                            reply += utilities.encodeIP((auth_servers[0].ip, auth_servers[0].port))
                            reply += utilities.encodeIP((auth_servers[0].ip, auth_servers[0].port))
                            
                elif binascii.b2a_hex(msg) == "1cb5aae840" : # Used for Subscription & CDKey Registration
                    log.info(clientid + "Sending out list of Auth Servers For Transactions")    
                    reply = manager.get_and_prep_server_list("authserver")    
                else :                 
                    log.info(clientid + "Sent unknown command: " + command + " Data: " + binascii.b2a_hex(msg))
                    reply == "\x00\x00"
                    
            elif command == "\x15" : # Log Processing Server's master server
                log.info(clientid + "Sending out list of Log Processing Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27021")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x09" : # system status master server
                log.info(clientid + "Sending out list of System Status Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27021")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x1D" : # BRS master server (Billing Bridge server?)
                log.info(clientid + "Sending out list of BRS Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27022")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x08" : # global transaction manager master server
                log.info(clientid + "Sending out list of Global Transaction Manager Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27022")))
                reply = struct.pack(">H", 1) + bin_ip                 
            elif command == "\x04" : # server configuration  master server
                log.info(clientid + "Sending out list of Server Configuration Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27022")))
                reply = struct.pack(">H", 1) + bin_ip             
            elif command == "\x01" : # administration authentication master server
                log.info(clientid + "Sending out list of Administration Authentication Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x11" : # administration billing bridge master server
                log.info(clientid + "Sending out list of Administration Billing Bridge Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x02" : # administration configuration master server
                log.info(clientid + "Sending out list of Administration Configuration Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip      
            elif command == "\x16" : # administration log processing master server
                log.info(clientid + "Sending out list of Administration Log Processing Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x13" : # administration authentication master server
                log.info(clientid + "Sending out list of Administration Authentication Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip              
            elif command == "\x0C" : # MCS Content Administration  master server
                log.info(clientid + "Sending out list of MCS Content Administration Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x17" : # CSER Administration master server
                log.info(clientid + "Sending out list of CSER Administration Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip
            elif command == "\x1B" : # VTS (validation ticket server) Administration master server
                log.info(clientid + "Sending out list of VTS Administration Master Servers")
                bin_ip = utilities.encodeIP((globalvars.serverip, int("27023")))
                reply = struct.pack(">H", 1) + bin_ip       
            else :
                 log.info(clientid + "Sent unknown command: " + command + " Data: " + binascii.b2a_hex(msg))
                 reply == "\x00\x00"
            clientsocket.send_withlen(reply)        
        else :
            log.error(clientid + "Invalid Message: " + binascii.b2a_hex(command))

        clientsocket.close()
        log.info (clientid + "disconnected from Directory Server")
       
    #takes care of removing any servers that have not responded within an hour,
    #the default heartbeat time is 30 minutes, so they had more than enough time to respond
    def expired_servers_thread(self):
        while True:
            time.sleep(3600) # 1 hour
            manager.remove_old_entries()
