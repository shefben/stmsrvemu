

import binascii
import logging
import os

import globalvars
from config import get_config as read_config
from utilities.packages import Package


ips_to_replace = [
    b"207.173.177.11:27030 207.173.177.12:27030",
    b"207.173.177.11:27030 207.173.177.12:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038",
    b"72.165.61.189:27030 72.165.61.190:27030 69.28.151.178:27038 69.28.153.82:27038 68.142.88.34:27038 68.142.72.250:27038",
    b"72.165.61.189:27030 72.165.61.190:27030 69.28.151.178:27038 69.28.153.82:27038 87.248.196.194:27038 68.142.72.250:27038",
    b"127.0.0.1:27030 127.0.0.1:27030 127.0.0.1:27030 127.0.0.1:27030 127.0.0.1:27030 127.0.0.1:27030",
    b"208.64.200.189:27030 208.64.200.190:27030 208.64.200.191:27030 208.78.164.7:27038"
]
config = read_config()

pkgadd_filelist = []
log = logging.getLogger("neuter")
def neuter_file(file, server_ip, server_port, filename, islan):

    # TODO Figure out how to also neuter game gcf's!
    # file = replace_bytes_in_file(file, b"WS2_32.dll", b"WS3_32.dll", filename)
    """if isinstance(filename, str):
        filename = filename.encode("latin-1")
    if file.startswith(b"\x3C\x68\x74\x6D\x6C\x3E"):
        file_temp = binascii.b2a_hex(file)
        i = 0
        file_new = b""
        for byte_index in range(0, len(file_temp), 2):
            byte_hex = file_temp[i:i + 2]
            if byte_hex == b"00":
                byte_hex = b""
            file_new += byte_hex
            i += 2
        file = binascii.a2b_hex(file_new)"""

    # Assuming replace_in_file is a function that takes the file, filename, search pattern, server_ip, server_port, and an index
    for index, search in enumerate(ips_to_replace) :
        file = replace_dirip_in_file(file, filename, search, server_ip, server_port, index % 5)

    file = replace_ips_in_file(file, filename, globalvars.ip_addresses, server_ip)

    if not config["server_ip"] == "127.0.0.1":
        file = replace_ips_in_file(file, filename, globalvars.loopback_ips, server_ip)

    if config["public_ip"] != "0.0.0.0" and filename != b"SteamNewLAN.exe" :
        fullstring = globalvars.replace_string(False)
    else :
        fullstring = globalvars.replace_string(True)

    file = config_replace_in_file(file, filename, fullstring, 1)

    if config["http_port"] != "steam" :
        if config["public_ip"] != "0.0.0.0" and filename != b"SteamNewLAN.exe" :
            fullstring1 = globalvars.replace_string_name_space(False)
            fullstring2 = globalvars.replace_string_name(False)
        else :
            fullstring1 = globalvars.replace_string_name_space(True)
            fullstring2 = globalvars.replace_string_name(True)

        file = config_replace_in_file(file, filename, fullstring1, 2)
        file = config_replace_in_file(file, filename, fullstring2, 3)
    return file


def replace_ips_in_file(file, filename, ip_list, replacement_ip) :
    if isinstance(filename, str):
        filename = filename.encode("latin-1")
    for ip in ip_list:
        loc = file.find(ip)
        if loc != -1 :
            if config["public_ip"] != "0.0.0.0" and not filename == b"SteamNewLAN.exe" :
                replacement_ip = config["public_ip"]
                replacement_ip = replacement_ip.encode( )
                replace_ip = replacement_ip + (b"\x00" * (16 - len(replacement_ip)))
                file = file[:loc] + replace_ip + file[loc + 16 :]
                log.debug(f"{filename.decode()}: Found and replaced IP {ip.decode():>16} at location {loc:08x}")
            else :
                replace_ip = replacement_ip.encode( ) + (b"\x00" * (16 - len(replacement_ip)))
                file = file[:loc] + replace_ip + file[loc + 16 :]
                log.debug(f"{filename.decode()}: Found and replaced IP {ip.decode():>16} at location {loc:08x}")
    return file


def config_replace_in_file(file, filename, replacement_strings, config_num):
    if isinstance(filename, str):
        filename = filename.encode("latin-1")
    for search, replace, info in replacement_strings:
        try:
            if file.find(search) != -1:
                if search == b"StorefrontURL1" and ":2004" in config["store_url"]:
                    file = file.replace(search, replace)
                    log.debug(f"{filename.decode()}: Replaced {info.decode()}")
                else:
                    missing_length = len(search) - len(replace)
                    if missing_length < 0:
                        log.warning(f"WARNING: Replacement text {replace.decode()} is too long! Not replaced!")
                    elif missing_length == 0:
                        file = file.replace(search, replace)
                        log.debug(f"{filename.decode()}: Replaced {info.decode()}")
                    else:
                        replace_padded = replace + (b'\x00' * missing_length)
                        file = file.replace(search, replace_padded)
                        log.debug(f"{filename.decode()}: Replaced {info.decode()}")
        except Exception as e:
            log.error(f"Config {config_num} line not found: {e} {filename.decode()}")

    return file


def replace_bytes_in_file(file, filename, search, replace) :
    if isinstance(filename, str):
        filename = filename.encode("latin-1")
    try :
        file = file.replace(search, replace)
        log.debug(f"{filename.decode()} replaced {search.decode()} with {replace.decode()} successfully")
        return file
    except Exception as e :
        log.error(f"An error occurred with {filename.decode()}: {e}")


def replace_dirip_in_file(file, filename, search, server_ip, server_port, dirgroup) :
    if isinstance(filename, str):
        filename = filename.encode("latin-1")
    if config["public_ip"] != "0.0.0.0" and not filename == b"SteamNewLAN.exe" :
        ip = (config["public_ip"] + ":" + server_port + " " + config["server_ip"] + ":" + server_port + " ").encode( )
    else :
        ip = (server_ip + ":" + server_port + " ").encode( )
    searchlength = len(search)
    iplength = len(ip)
    numtoreplace = searchlength // iplength
    ips = ip * numtoreplace
    replace = ips + (b'\x00' * (searchlength - len(ips)))
    if file.find(search) != -1 :
        file = file.replace(search, replace)
        log.debug(f"{filename}: Replaced directory server IP group {dirgroup}")
    return file


def get_filenames():
    if globalvars.steamui_ver < 252: #last 2006 for now
        return (b"SteamNew.exe",b"Steam.dll",b"SteamUI.dll",b"platform.dll",b"steam\SteamUI.dll",b"friends\servers.vdf",b"servers\MasterServers.vdf",b"servers\ServerBrowser.dll",b"Public\Account.html",b"caserver.exe",b"cacdll.dll",b"CASClient.exe",b"unicows.dll",b"GameUI.dll",b"steamclient.dll", b"steam\SteamUIConfig.vdf")
    else:
        return (b"SteamNew.exe",b"Steam.dll",b"SteamUI.dll",b"platform.dll",b"steam\SteamUI.dll",b"friends\servers.vdf",b"servers\MasterServers.vdf",b"servers\ServerBrowser.dll",b"Public\Account.html",b"caserver.exe",b"cacdll.dll",b"CASClient.exe",b"unicows.dll",b"GameUI.dll")#,b"steamclient.dll",b"GameOverlayUI.exe",b"serverbrowser.dll",b"gamoverlayui.dll",b"steamclient64.dll",b"AppOverlay.dll",b"AppOverlay64.dll",b"SteamService.exe",b"friendsUI.dll",b"SteamService.dll")


def neuter(pkg_in, pkg_out, server_ip, server_port, islan):
    log = logging.getLogger("neuter")
    f = open(pkg_in, "rb")
    pkg = Package(f.read())
    f.close()

    for filename in get_filenames():
        if filename in pkg.filenames:
            file = pkg.get_file(filename)
            file = neuter_file(file, server_ip, server_port, filename, islan)
            pkg.put_file(filename, file)
    if len(pkgadd_filelist) > 0:
        del pkgadd_filelist[:]

    if config["use_sdk"] == "0" and config["sdk_ip"] != "0.0.0.0":
        sdk_line = 'SdkContentServerAdrs = "' + config["sdk_ip"] + ":" + config["sdk_port"] + '"'
        with open("files/pkg_add/steamui/Steam.cfg", "w") as f:
            f.write(sdk_line)
    else:
        try:
            os.remove("files/pkg_add/steamui/Steam.cfg")
        except:
            pass

    if os.path.isdir("files/pkg_add/"):
        log.debug("Found pkg_add folder")
        if os.path.isdir("files/pkg_add/steamui/") and ("SteamUI_" in pkg_in):
            log.debug("Found steamui folder")
            path_to_remove = "files/pkg_add/steamui/"
            recursive_pkg("files/pkg_add/steamui/")
            log.debug(f"Number of files to add to SteamUI: {str(len(pkgadd_filelist))}")
            for filename_extra in pkgadd_filelist:
                file2 = open(filename_extra, "rb")
                filedata = file2.read()
                file2.close()
                filename_extra = filename_extra[len(path_to_remove):]
                pkg.put_file(filename_extra, filedata)
        elif os.path.isdir("files/pkg_add/steam/") and ("Steam_" in pkg_in):
            log.debug("Found steam folder")
            path_to_remove = "files/pkg_add/steam/"
            recursive_pkg("files/pkg_add/steam/")
            log.debug(f"Number of files to add to Steam: {str(len(pkgadd_filelist))}")
            for filename_extra in pkgadd_filelist:
                file2 = open(filename_extra, "rb")
                filedata = file2.read()
                file2.close()
                filename_extra = filename_extra[len(path_to_remove):]
                pkg.put_file(filename_extra, filedata)

    f = open(pkg_out, "wb")
    f.write(pkg.pack())
    f.close()


def recursive_pkg(dir_in):
    files = os.listdir(dir_in)
    for filename_extra in files:
        if os.path.isfile(os.path.join(dir_in, filename_extra)):
            pkgadd_filelist.append(os.path.join(dir_in, filename_extra))
        elif os.path.isdir(os.path.join(dir_in, filename_extra)):
            recursive_pkg(os.path.join(dir_in, filename_extra))