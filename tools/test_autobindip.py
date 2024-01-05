import configparser
import socket


def get_server_ip():
    """Get the server's IP address."""
    try:
        # Connect to an external address (doesn't actually establish a connection)
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's DNS, used just to get the socket's name
            return s.getsockname()[0]
    except Exception as e:
        print(f"Error obtaining IP address: {e}")
        return None


def write_ip_to_config(ip_address, config_file = 'emulator.ini'):
    """Write the server's IP address to the configuration file."""
    config = configparser.ConfigParser()
    config.read(config_file)

    if 'Server' not in config:
        config['Server'] = {}

    config['Server']['server_ip'] = ip_address

    with open(config_file, 'w') as configfile:
        config.write(configfile)


def main():
    ip_address = get_server_ip()
    if ip_address:
        print(f"Detected IP Address: {ip_address}")
        write_ip_to_config(ip_address)
        print(f"IP Address written to {config_file}")
    else:
        print("Could not detect the IP address.")


if __name__ == "__main__":
    main()