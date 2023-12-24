import logging
import os
import subprocess
import threading
import time

# from scalene import scalene_profiler
import dirs
import logger
import globalvars

from config import get_config as read_config
from globalvars import local_ver
from servers.authserver import authserver
from servers.beta_authserver import Beta1_AuthServer
from servers.beta_contentserver import Beta1_ContentServer
from servers.clientupdateserver import clientupdateserver
from servers.cmserver import cmserver, cmserver2
from servers.configserver import configserver
from servers.contentlistserver import contentlistserver
from servers.contentserver import contentserver
from servers.cserserver import CSERServer
from servers.directoryserver import directoryserver
from servers.masterserver import MasterServer
# from servers.authserverv3 import authserverv3
from servers.validationserver import validationserver
from servers.vttserver import vttserver
from servers.trackerserver_beta2 import TrackerServer
from steamweb.ftp import create_ftp_server
from steamweb.steamweb import check_child_pid
from steamweb.steamweb import steamweb
from servers.valve_anticheat1 import VAC1Server
from utilities.filesystem_monitor import DirectoryMonitor, GCFFileHandler
from utilities.inputmanager import start_watchescape_thread
from utils import flush_cache, parent_initializer

globalvars.aio_server = True

# start watching for 'esc' keyboard key
start_watchescape_thread()

# create directories
dirs.create_dirs()

# TODO uncomment for release
# clear the console of any garbage from previous commands
# clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
# clearConsole()

# initialize logger
logger.init_logger()
log = logging.getLogger('emulator')

# read the configuration file (emulator.ini)
config = read_config()

# flush cache if emulator.ini has changed
flush_cache()

print("")
print(f"Steam 2002-2011 Server Emulator v{local_ver}")
print(("=" * 33) + ("=" * len(local_ver)))
print()
print(" -== Steam 20th Anniversary Edition 2003-2023 ==-")
print()

new_password = parent_initializer()

log.info("   ---Starting Steam Server---   ")

dirserver = directoryserver(int(config["dir_server_port"]), config)
dirserver.daemon = True
dirserver.start()
# launch directoryserver first so server can heartbeat the moment they launch
if globalvars.dir_ismaster == "true":
	log.info(f"Steam Master General Directory Server listening on port {str(config['dir_server_port'])}")
else:
	log.info(f"Steam Slave General Directory Server listening on port {str(config['dir_server_port'])}")


contentlistserver(int(config["contentdir_server_port"]), config).start()
log.info(f"Steam2 Content List Server listening on port {str(config['contentdir_server_port'])}")


csserver = contentserver(int(config["content_server_port"]), config)
csserver.daemon = True
csserver.start()
log.info(f"Steam2 Content Server listening on port {str(config['content_server_port'])}")


clientupdateserver(int(config["clupd_server_port"]), config).start()
log.info(f"Steam2 Client Update Server listening on port {str(config['clupd_server_port'])}")


configserver(int(config["config_server_port"]), config).start()
log.info(f"Steam2 Config Server listening on port {str(config['config_server_port'])}")


authsrv = authserver(int(config["auth_server_port"]), config)
authsrv.daemon = True
authsrv.start()
log.info(f"Steam2 Master Authentication Server listening on port {str(config['auth_server_port'])}")


CSERServer(int(config["cser_server_port"]), config).start()
log.info(f"Steam2 Client Stats & Error Reporting Server listening on port {str(config['cser_server_port'])}")


validationserver(int(config["validation_port"]), config).start()
log.info(f"Steam2 User Validation Server listening on port {str(config['validation_port'])}")


MasterServer(int(config["masterhl1_server_port"]), config).start()
log.info(f"Steam2 Master Server listening on port {str(config['masterhl1_server_port'])}")


"""MasterHL(int(config["masterhl1_server_port"]), config).start()
log.info(f"Master HL1 Server listening on port {str(config['masterhl1_server_port'])}")


MasterHL2(int(config["masterhl2_server_port"]), config).start()
log.info(f"Master HL2 Server listening on port {str(config['masterhl2_server_port'])}")


MasterRDKF(int(config["masterrdkf_server_port"]), config).start()
log.info(f"Master RDKF Server listening on port {str(config['masterrdkf_server_port'])}")"""


# trackerserver(int(config["tracker_server_port"]), config).start()
# log.info(f"[2004-2007] Tracker Server listening on port {str(config['tracker_server_port'])}")
# globalvars.tracker = 1
# time.sleep(1)

# cmserver(int(config["cmserver_port"]), config).start()
# log.info("Steam3 CM Server 1 listening on port 27014")
# 

vttserver(config["vtt_server_port1"], config).start()
log.info(f"Valve Time Tracking Server listening on port {str(config['vtt_server_port1'])}")


vttserver(config["vtt_server_port2"], config).start()
log.info(f"Valve CyberCafe server listening on port {str(config['vtt_server_port2'])}")

if config["enable_steam3_servers"].lower() == "true":
	cmserver(27014, config).start()
	cmserver2(27017, config).start()
	globalvars.tracker = 0
	log.info(f"Steam3 Connection Manager Server's 1 and 2 listening on port 27014 and 27017 TCP and UDP")
else:
	if globalvars.record_ver == 1:
		globalvars.tracker = 1
		TrackerServer(1200, config).start()
		log.info("Started 2003 TRACKER server on port 1200")
		log.info("Made by ymgve")
	else:
		log.info("TRACKER unsupported on release client, not started")

	if int(globalvars.steam_ver) <= 14:
		vacserver = VAC1Server(int(config["vac_server_port"]), config)
		vacserver.daemon = True
		vacserver.start()
		log.info(f"Steam2 Valve Anti-Cheat Server listening on port {str(config['content_server_port'])}")


if config["use_webserver"].lower() == "true" and os.path.isdir(config["apache_root"]):
	if globalvars.steamui_ver < 87 or config["http_port"] == "steam" or config["http_port"] == "0":
		steamweb("80", config["http_ip"], config["apache_root"], config["web_root"])
		http_port = "80"
	else:
		steamweb(config["http_port"], config["http_ip"], config["apache_root"], config["web_root"])
		http_port = str(config["http_port"])  # [1:]
	log.info(f"Steam Web Server listening on port {http_port}")
	find_child_pid_timer = threading.Timer(10.0, check_child_pid()).start()
elif config["use_webserver"] == "true" and not os.path.isdir(config["apache_root"]):
		log.error("Cannot start Steam Web Server: apache folder is missing")

if config["sdk_ip"] != "0.0.0.0":
	log.info(f"Steamworks SDK Content Server configured on port {str(config['sdk_port'])}")

if globalvars.record_ver == 0:
	log.info(f"Starting 2002 Beta 1 Authentication Server on port 5273")
	Beta1_AuthServer(5273, config).start()

	log.info(f"Starting 2002 Beta 1 Content Server on port 12345")
	Beta1_ContentServer(12345, config).start()

	log.info(f"Starting 2002 Beta 1 Update FTP Server on port 21")
	threading.Thread(target=create_ftp_server, args=("files/beta1_ftp",)).start()

log.debug(f"TGT set to version {globalvars.tgt_version}")

if config["http_port"].lower() == "steam":
	log.info("...Steam Server ready using Steam DNS...")
else:
	log.info("...Steam Server ready...")

if new_password == 1:
	log.info("New Peer Password Generated: \033[1;33m{}\033[0m".format(globalvars.peer_password))
	log.info("Make sure to give this password to any servers that may want to add themselves to your network!")

# Monitor to convert gcf files in the background when they are added to the convert folder while server is running
gcf_handler = GCFFileHandler()
directory_monitor = DirectoryMonitor("files/convert/", gcf_handler)
directory_monitor.start()

# input_buffer = ""
time.sleep(1) # This is needed for the following line to show up AFTER the sever initialization information
print("Press Escape to exit...")

"""class EmuInputManager(InputManager):
	def process_input(self, c):
		if c == '\r':
			if self.input_buffer.strip() == 'showdirlist':
				print(" ")
				dirmanager.print_dirserver_list()
			elif self.input_buffer.strip() == 'showcslist':
				print(" ")
				csdsmanager.print_contentserver_list()
			elif self.input_buffer.strip() == 'exit' or self.input_buffer.strip() == 'quit':
				os._exit(0)
			else :
				print("\n Unknown Command:  " + self.input_buffer)
			self.input_buffer = ''
		elif c == '\x08':
			if self.input_buffer:
				# Clear the last character on the screen
				sys.stdout.write('\b ')
				sys.stdout.flush()
				# Remove the last character
				self.input_buffer = self.input_buffer[:-1]
		elif c == b'\x1b':
			os._exit(0)
		else:
			self.input_buffer += c # this allows for more than 1 character at a time
"""
# input_manager = EmuInputManager()
# input_manager.start_input()