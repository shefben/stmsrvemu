import threading, logging, time, os, os.path, msvcrt
import utilities, globalvars, emu_socket
import steamemu.logger
import python_check

from steamemu.authserver import authserver
from steamemu.config import save_config_value
from steamemu.config import read_config

config = read_config()

# Check the Python version
python_check.check_python_version()

#check for a peer_password, otherwise generate one
new_password = utilities.check_peerpassword()

def watchescape_thread():       
    while True:
        if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:  # 27 is the ASCII code for Escape
            os._exit(0)
            
thread2 = threading.Thread(target=watchescape_thread)
thread2.daemon = True
thread2.start()
        
print("Steam 2004-2011 Authentication Server Emulator v" + globalvars.emuversion)
print("=====================================")
print
print("**************************")
print("Server IP: " + config["server_ip"])
if config["public_ip"] != "0.0.0.0" :
    print("Public IP: " + config["public_ip"])
print("**************************")
print

#check local ip and set globalvars.serverip
utilities.checklocalipnet()

log = logging.getLogger('AuthSRV')
log.info("...Starting Steam Server...\n")
  
#grab the ip and port for id ticket validation server
globalvars.validation_ip   = config["validation_ip"]
globalvars.validation_port = int(config["validation_server_port"])


log.info("Steam Master Authentication Server listening on port " + str(config["auth_server_port"]))
time.sleep(0.5) #give us a little more time than usual to make sure we are initialized before servers start their heartbeat

authserver(int(config["auth_server_port"]), config).start()  

log.info("Steam Authentication Server is ready.")

if new_password == 1 :
    log.info("New Peer Password Generated: \033[1;33m{}\033[0m".format(globalvars.peer_password))
    log.info("Make sure to give this password to any servers that may want to add themselves to your network!")

print("Press Escape to exit...")


