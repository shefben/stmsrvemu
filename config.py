import configparser  # , logging

# Read the configuration once and store it in a global variable
config_data = []


def get_config():
    return config_data


def read_config():
    # log = logging.getLogger("root")

    # log.info("Reloading config")

    myDefaults = {'public_ip': "0.0.0.0", 'log_level': 'logging.INFO', 'log_to_file': "true", 'hldsupkg': "", 'steamver': "v2",
                  'default_password': "password", 'v2storagedir': "files/v2storages/", 'storagedir': "files/storages/",
                  'manifestdir': "files/manifests/", 'v2manifestdir': "files/v2manifests/", "packagedir": 'files/packages/',
                  'tinserver': "0", 'tracker_ip': "0.0.0.0", 'cafeuser': "noaccountconfigured", 'cafepass': "bar",
                  'cafemacs': "00-00-00-00-00-00;", 'cafetime': "60", 'cafe_use_mac_auth': "false", 'sdk_ip': "0.0.0.0",
                  'sdk_port': "27030", 'use_sdk': "0", 'tgt_version': "2", 'dir_ismaster': "true", 'peer_password': "", 'enable_whitelist': "False",
                  'enable_blacklist': "False", 'smtp_enabled': "true", 'smtp_server': "", 'smtp_port': "", 'smtp_username': "", 'smtp_security': "tls",
                  'smtp_password': "", 'validation_port': "27040", 'database': "stmserver.db", 'database_type': "sqlite", 'database_username': "root",
                  'database_password': "", 'database_database': "stmserver", 'database_host': "localhost",  'contentdir_server_port': "27030",
                  'csds_ipport': "127.0.0.1:27037", 'database_port': "3306", 'cellid': "2", 'masterdir_ipport': "127.0.0.1:27038", 'cs_region': "US",
                  'main_key_n': "0x86724794f8a0fcb0c129b979e7af2e1e309303a7042503d835708873b1df8a9e307c228b9c0862f8f5dbe6f81579233db8a4fe6ba14551679ad72c01973b5ee4ecf8ca2c21524b125bb06cfa0047e2d202c2a70b7f71ad7d1c3665e557a7387bbc43fe52244e58d91a14c660a84b6ae6fdc857b3f595376a8e484cb6b90cc992f5c57cccb1a1197ee90814186b046968f872b84297dad46ed4119ae0f402803108ad95777615c827de8372487a22902cb288bcbad7bc4a842e03a33bd26e052386cbc088c3932bdd1ec4fee1f734fe5eeec55d51c91e1d9e5eae46cf7aac15b2654af8e6c9443b41e92568cce79c08ab6fa61601e4eed791f0436fdc296bb373",
                  'main_key_e': "0x07e89acc87188755b1027452770a4e01c69f3c733c7aa5df8aac44430a768faef3cb11174569e7b44ab2951da6e90212b0822d1563d6e6abbdd06c0017f46efe684adeb74d4113798cec42a54b4f85d01e47af79259d4670c56c9c950527f443838b876e3e5ef62ae36aa241ebc83376ffde9bbf4aae6cabea407cfbb08848179e466bcb046b0a857d821c5888fcd95b2aae1b92aa64f3a6037295144aa45d0dbebce075023523bce4243ae194258026fc879656560c109ea9547a002db38b89caac90d75758e74c5616ed9816f3ed130ff6926a1597380b6fc98b5eeefc5104502d9bee9da296ca26b32d9094452ab1eb9cf970acabeecde6b1ffae57b56401",
                  'net_key_n': "0xbf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059",
                  'net_key_d': "0x4ee3ec697bb34d5e999cb2d3a3f5766210e5ce961de7334b6f7c6361f18682825b2cfa95b8b7894c124ada7ea105ec1eaeb3c5f1d17dfaa55d099a0f5fa366913b171af767fe67fb89f5393efdb69634f74cb41cb7b3501025c4e8fef1ff434307c7200f197b74044e93dbcf50dcc407cbf347b4b817383471cd1de7b5964a9d",
                  'v3storagedir2': "files/v3storages2/", 'v3manifestdir2': "files/v3manifests2/", 'vac_server_port': "27012",
                  'store_url_new': "/storefront", 'support_url_new': "/support", 'http_port': "80", 'universe': "1",
                  'apache_root': "files/webserver/apache24", 'web_root': "files/webserver/webroot", 'reset_clears_client': "false",
                  'use_webserver': "true", 'http_ip': "", 'emu_auto_update': "true", 'clupd_server_port': "27031",
                  'betamanifestdir': "", 'betastoragedir': "", 'server_sm': "255.255.255.0", 'server_ip': "127.0.0.1",
                  'steam_date': "2004/10/01", 'steam_time': "00:14:03", 'enable_steam3_servers': "false", 'auto_public_ip': "True", 'use_file_blobs': "true",
                  'auto_server_ip': "True", 'harvest_ip': "0.0.0.0", 'allow_harvest_upload': "True", 'harvest_server_port': "27032",
                  'support_email': "admin@stmserver", 'network_name': "STMServer", 'http_maxconnections':"20", 'http_signature': "STMServer Network",
                  'friends_server_port': "27014", 'cm_server_port': "27017", 'cser_server_port': "27013", 'vtt_server_port1': "27046",
                  'vtt_server_port2': "27047", 'show_convert_bar': "True", 'network_logo': "", 'email_location_support': "false",
                  'amount_of_suggested_names': "10", 'use_builtin_suggested_name_modifiers': "true"}

    c = configparser.SafeConfigParser(myDefaults)
    c.read("emulator.ini")

    values = {}

    for name, value in c.items("config"):
        # Remove comments and extra spaces or tabs
        value = value.split(';')[0].strip()
        values[name] = value

    return values


config_data = read_config()


def save_config_value(key, value, old_key=None):
    file_path = 'emulator.ini'

    # Read the existing content of the file
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Check if the old_key or key already exists
    key_exists = False
    for i, line in enumerate(lines):
        # Check for the key (active or commented)
        if ((old_key and line.startswith(old_key + '=')) or
            line.startswith(key + '=') or
            line.lstrip().startswith(';' + key + '=')):
            # If key is commented, remove the comment
            if line.lstrip().startswith(';' + key + '='):
                line = line.lstrip()[1:]

            # Replace the line with new key and value
            lines[i] = key + '=' + value + '\n'
            key_exists = True
            break

    # If the key doesn't exist, add it as a new line
    if not key_exists:
        lines.append(key + '=' + value + '\n')

    # Write the modified content back to the file
    with open(file_path, 'w') as file:
        file.writelines(lines)