import logging
import msvcrt
import os
import shutil
import subprocess
import sys
import threading
import time


#from scalene import scalene_profiler
import utilities.error_catcher
import dirs
import logger
import globalvars
import utils

from config import get_config as read_config
from globalvars import local_ver, update_exception1, update_exception2
from servers.authserver import authserver
from servers.clientupdateserver import clientupdateserver
from servers.configserver import configserver
from servers.contentlistserver import contentlistserver
from servers.contentserver import contentserver
from servers.cserserver import CSERServer
from servers.directoryserver import directoryserver
from servers.friends import friends
from servers.masterserver import MasterServer
# from servers.authserverv3 import authserverv3
from servers.validationserver import validationserver
from servers.vttserver import vttserver
from steamweb.steamweb import check_child_pid
from steamweb.steamweb import steamweb
from utilities.converter import convertgcf


mod_date_emu = os.path.getmtime("emulator.exe")
try:
    mod_date_cach = os.path.getmtime("files/cache/emulator.ini.cache")
except:
    mod_date_cach = 0

# TODO uncomment for release
# clearConsole = lambda: os.system('cls' if os.name in ('nt', 'dos') else 'clear')
# clearConsole()

if (mod_date_cach < mod_date_emu) and globalvars.clear_config == True:
    #print("Config change detected, flushing cache...")
    try:
        shutil.rmtree("files/cache")
    except:
        pass

# create directories
dirs.create_dirs()

def watchescape_thread():
    while True:
        if ord(msvcrt.getch()) == 27:
            os._exit(0)


thread2 = threading.Thread(target=watchescape_thread)
thread2.daemon = True
thread2.start()

# test code, using a library for watching for escape key.  performance is the same as the current escape key loop above.
"""def on_esc_press():
    print("ESC key pressed. Exiting...")
    os._exit(0)  # Or perform any other action you'd like

# Register the hotkey
keyboard.add_hotkey('esc', on_esc_press)"""


config = read_config()

print("")
print(f"Steam 2003-2011 Server Emulator v {local_ver}")
print(("=" * 33) + ("=" * len(local_ver)))
print("")
print(" -== Steam 20th Anniversary Edition 2003-2023 ==-")
print("")

globalvars.aio_server = True

globalvars.cs_region = config["cs_region"]
globalvars.dir_ismaster = config["dir_ismaster"]

globalvars.server_ip = config["server_ip"]
globalvars.server_ip_b = globalvars.server_ip.encode("latin-1")

globalvars.public_ip = config["public_ip"]

logger.init_logger()
log = logging.getLogger('emulator')

utils.initialize(log)

if not globalvars.update_exception1 == "":
    log.debug("Update1 error: " + str(update_exception1))
if not globalvars.update_exception2 == "":
    log.debug("Update2 error: " + str(update_exception2))

log.info("...Starting Steam Server...")

utils.finalinitialize(log)

# check for a peer_password, otherwise generate one
new_password = utils.check_peerpassword()

log.info("Checking for gcf files to convert...")
if config["show_convert_bar"].lower() == "true":
    globalvars.hide_convert_prints = True

convertgcf()


globalvars.hide_convert_prints = False


directoryserver(int(config["dir_server_port"]), config).start()
# launch directoryserver first so server can heartbeat the moment they launch
if globalvars.dir_ismaster == "true":
    log.info("Steam Master General Directory Server listening on port " + str(config["dir_server_port"]))
else:
    log.info("Steam Slave General Directory Server listening on port " + str(config["dir_server_port"]))


contentlistserver(int(config["contentdir_server_port"]), config).start()
log.info("Steam2 Content List Server listening on port " + str(config["contentdir_server_port"]))


contentserver(int(config["content_server_port"]), config).start()
log.info("Steam2 Content Server listening on port " + str(config["content_server_port"]))


clientupdateserver(int(config["clupd_server_port"]), config).start()
log.info("Steam2 Client Update Server listening on port " + str(config["clupd_server_port"]))


configserver(int(config["config_server_port"]), config).start()
log.info("Steam2 Config Server listening on port " + str(config["config_server_port"]))


authserver(int(config["auth_server_port"]), config).start()
log.info("Steam2 Master Authentication Server listening on port " + str(config["auth_server_port"]))


CSERServer(int(config["cser_server_port"]), config).start()
log.info("Steam2 CSER Server listening on port " + str(config["cser_server_port"]))


validationserver(int(config["validation_port"]), config).start()
log.info("Steam2 User Validation Server listening on port " + str(config["validation_port"]))

MasterServer(int(config["masterhl1_server_port"]), config).start()
log.info("Steam2 Master Server listening on port " + str(config["masterhl1_server_port"]))

"""MasterHL(int(config["masterhl1_server_port"]), config).start()
log.info("Master HL1 Server listening on port " + str(config["masterhl1_server_port"]))


MasterHL2(int(config["masterhl2_server_port"]), config).start()
log.info("Master HL2 Server listening on port " + str(config["masterhl2_server_port"]))


MasterRDKF(int(config["masterrdkf_server_port"]), config).start()
log.info("Master RDKF Server listening on port " + str(config["masterrdkf_server_port"]))"""


# trackerserver(int(config["tracker_server_port"]), config).start()
# log.info("[2004-2007] Tracker Server listening on port " + str(config["tracker_server_port"]))
# globalvars.tracker = 1
# time.sleep(1)

# cmserver(int(config["cmserver_port"]), config).start()
# log.info("Steam3 CM Server 1 listening on port 27014")
# 

vttserver(config["vtt_server_port1"], config).start()
log.info("Valve Time Tracking Server listening on port " + str(config["vtt_server_port1"]))


vttserver(config["vtt_server_port2"], config).start()
log.info("Valve CyberCafe server listening on port " + str(config["vtt_server_port2"]))

if config["enable_steam3_servers"] == "1":
    # cmserver2(int(config["cm_server_port2"]), friends, config).start()
    globalvars.tracker = 0
    log.info("Steam3 Connection Manager Server listening on port " + config["cm_server_port2"])
else:
    if globalvars.record_ver == 1 :
        globalvars.tracker = 1
        subprocess.Popen("trackerserver.exe")
        log.info("Started 2003 TRACKER server on port 1200")
    else :
        log.info("TRACKER unsupported on release client, not started")


if config["use_webserver"].lower() == "true":
    if globalvars.steamui_ver < 87 or config["http_port"] == "steam" or config["http_port"] == "0":
        steamweb("80", config["http_ip"], config["apache_root"], config["web_root"])
        http_port = "80"
    else:
        steamweb(config["http_port"], config["http_ip"], config["apache_root"], config["web_root"])
        http_port = str(config["http_port"])  # [1:]
    log.info("Steam Web Server listening on port " + http_port)
    find_child_pid_timer = threading.Timer(10.0, check_child_pid()).start()
    

if config["sdk_ip"] != "0.0.0.0":
    log.info("Steamworks SDK Content Server configured on port " + str(config["sdk_port"]))
    

log.debug("TGT set to version " + globalvars.tgt_version)

if config["http_port"].lower() == "steam":
    log.info("...Steam Server ready using Steam DNS...")
else:
    log.info("...Steam Server ready...")

if new_password == 1:
    log.info("New Peer Password Generated: \033[1;33m{}\033[0m".format(globalvars.peer_password))
    log.info("Make sure to give this password to any servers that may want to add themselves to your network!")

input_buffer = ""
print("Press Escape to exit...")

# Keep the script running
# keyboard.wait('esc')