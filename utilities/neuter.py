

import binascii
import logging
import os

import globalvars
from config import get_config as read_config
from utilities import encryption
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

def neuter_beta1(file_path):
    # Byte string to search for
    original_berstring = bytes([
        0x30, 0x81, 0x9D, 0x30, 0x0D, 0x06, 0x09, 0x2A, 0x86, 0x48, 0x86, 0xF7,
        0x0D, 0x01, 0x01, 0x01, 0x05, 0x00, 0x03, 0x81, 0x8B, 0x00, 0x30, 0x81,
        0x87, 0x02, 0x81, 0x81, 0x00, 0xDA, 0xDE, 0x57, 0xFE, 0x10, 0x99, 0xF9,
        0x4B, 0x81, 0xB9, 0x0D, 0x00, 0x82, 0x50, 0x5B, 0xE3, 0x74, 0xCA, 0x97,
        0x28, 0xAB, 0x9A, 0x88, 0x5B, 0x3B, 0x0E, 0x8E, 0x02, 0x5E, 0x43, 0xE5,
        0xCC, 0xD8, 0x1B, 0x00, 0xCD, 0xBD, 0x05, 0xE2, 0x2A, 0xC2, 0x5C, 0x53,
        0x18, 0xBF, 0x84, 0xC3, 0x40, 0x21, 0x42, 0xA5, 0xC3, 0x8A, 0xC3, 0xF4,
        0x27, 0x1B, 0xAB, 0xC3, 0xE5, 0xC0, 0x60, 0x18, 0xED, 0x26, 0x57, 0xF4,
        0x68, 0xC5, 0xDA, 0x55, 0xAA, 0x7E, 0x3B, 0x3B, 0x1A, 0xB2, 0x72, 0x06,
        0x17, 0x4A, 0x85, 0x6E, 0xE2, 0xB6, 0x73, 0x91, 0x9D, 0xEB, 0x47, 0xBD,
        0x49, 0x1D, 0x10, 0x21, 0x3E, 0x90, 0xDB, 0xD5, 0x6E, 0x25, 0x2C, 0xC6,
        0xC9, 0xE9, 0x18, 0x8D, 0x0B, 0xC5, 0x71, 0x9B, 0x57, 0xED, 0x57, 0x02,
        0xC6, 0x45, 0x5F, 0x27, 0x31, 0x6A, 0xA0, 0xAA, 0x03, 0x78, 0x2F, 0x06,
        0xDF, 0x02, 0x01, 0x11
    ])
    original_ascii_key = b"30819d300d06092a864886f70d010101050003818b0030818702818100bc265d3402562c8afb78904e7ec84ee5b6662a09216b6b50da4205094c54f8b09d211bdeb8219ca4df67e39d2349bcbe9cb3b0d1e18b23cf33b5b51cabbeaa529a27e2b3928bdbe1c5c5a7de6bee7e87aecfa26f82286cad35df7ee53fe12adb2d1e81e98ca5faa6db509de8c4f482fa3c4fcf875ce21d443ed635bbdcb425db020111"

    new_ascii_key = b"30819d300d06092a864886f70d010101050003818b0030818702818100bf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059020111"

    original_ip = b"63.251.171.132"


    if (config[public_ip] != "0.0.0.0"):
        serverip = config['public_ip']
    else:
        serverip = config['server_ip']

    if len(serverip) > 15:
        log.error(f'Server_IP Larger than 15 bytes!!! ip: {serverip}  length: {len(serverip)}')
        os.exit()

    new_ip = serverip.encode('latin-1') + b"\x00"
    try:
        # Read the file
        with open(file_path, 'rb') as file:
            file_data = file.read()
        BERstring = encryption.network_key.public_key( ).export_key("DER")
        # Replace the byte string
        file_data = file_data.replace(original_berstring, BERstring, 1)
        file_data = file_data.replace(original_ascii_key, new_ascii_key, 1)
        file_data = file_data.replace(original_ip, new_ip, 1)
        # Write the modified content back to the file
        with open(file_path, 'wb') as file:
            file.write(file_data)

        print(f"File '{file_path}' has been updated.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def recursive_pkg(dir_in):
    files = os.listdir(dir_in)
    for filename_extra in files:
        if os.path.isfile(os.path.join(dir_in, filename_extra)):
            pkgadd_filelist.append(os.path.join(dir_in, filename_extra))
        elif os.path.isdir(os.path.join(dir_in, filename_extra)):
            recursive_pkg(os.path.join(dir_in, filename_extra))