import socket
import struct
import time
import threading

# Challanges list to store IP addresses and their respective challenges
challanges = []

# Server list to store server information
server = []

# Locks for thread-safe access to the lists
challanges_lock = threading.Lock()
server_lock = threading.Lock()

def generate_challenge():
    return struct.unpack('<i', os.urandom(4))[0]

def remove_expired_challenges():
    with challanges_lock:
        current_time = time.time()
        challanges[:] = [entry for entry in challanges if current_time - entry['time'] <= 600]

def check_challenge(ip, challenge_str):
    with challanges_lock:
        for entry in challanges:
            if entry['ip'] == ip:
                if str(entry['challenge']) == challenge_str:
                    return 1
                else:
                    return 0
    return -1


def handle_getchallenge(client_socket, client_address):
    # Check if there is an existing challenge for the client IP
    challenge_result = check_challenge(client_address[0], "")
    if challenge_result == -1:
        # No challenge entry for this IP, generate a new challenge
        challenge = generate_challenge()
        with challanges_lock:
            challanges.append(
                {'ip': client_address[0], 'challenge': challenge, 'time': time.time()})
    else:
        challenge = challenge_result

    # Send the challenge back to the client
    packet = b'\xff\xff\xff\xffs\n' + struct.pack('<i', challenge) + '\n'
    client_socket.sendto(packet, client_address)

def handle_heartbeat2(client_socket, request_data, client_address):
    if len(request_data) != 41:
        # Invalid packet format, send an error response
        response = b'\xff\xff\xff\xffl\nBad Format\n'
        client_socket.sendto(response, client_address)
        return

    received_challenge = struct.unpack('<i', request_data[11:15])[0]
    result = check_challenge(client_address[0], str(received_challenge))

    if result == -1:
        # No challenge entry for this IP, send an error response
        response = b'\xff\xff\xff\xffl\nNo challenge for your address.\n'
        client_socket.sendto(response, client_address)
        return
    elif result == 0:
        # Invalid challenge for this IP, send an error response
        response = b'\xff\xff\xff\xffl\nBad Challenge\n'
        client_socket.sendto(response, client_address)
        return

    # Extract information from the heartbeat packet
    info_dict = {}
    try:
        parts = request_data.split('\\')
        for i in range(1, len(parts) - 1, 2):
            info_dict[parts[i]] = parts[i + 1]
    except IndexError:
        # Invalid packet format, send an error response
        response = b'\xff\xff\xff\xffl\nBad Format\n'
        client_socket.sendto(response, client_address)
        return

    # Create a new entry for the server list
    server_entry = {
        'num': int(info_dict.get('num', 0)),
        'maxplayers': int(info_dict.get('max', 0)),
        'bots': int(info_dict.get('bots', 0)),
        'challenge': received_challenge,
        'gamedir': info_dict.get('gamedir', ''),
        'map': info_dict.get('map', ''),
        'type': info_dict.get('type', ''),
        'password': int(info_dict.get('password', 0)),
        'os': info_dict.get('os', ''),
        'secure': int(info_dict.get('secure', 0)),
        'lan': int(info_dict.get('lan', 0)),
        'version': info_dict.get('version', ''),
        'info': info_dict.get('info', ''),
        'bNewServer': True,
        'protocol': int(info_dict.get('protocol', 0)),
        'product': info_dict.get('product', ''),
        'region': int(info_dict.get('region', 255)),
        'players': int(info_dict.get('players', 0)),
        'proxy': int(info_dict.get('proxy', 0)),
        'uniqueid': struct.unpack('<i', os.urandom(4))[0],  # Generate random unique id
        'time': time.time(),  # Current timestamp
        'ip': client_address[0],
        'port': client_address[1]
    }

    # Check if the server is already in the list
    for entry in server:
        if entry['ip'] == server_entry['ip'] and entry['port'] == server_entry['port']:
            return  # Server already in the list, do nothing

    # Add the server entry to the server list
    with server_lock:
        server.append(server_entry)

def handle_getbatch(client_socket, request_data):
    ip_filter = request_data[:4]
    filter_info = request_data[4:]

    response_packet = b'\xff\xff\xff\xfff\n'

    def append_server_to_response(server_entry):
        ip_parts = server_entry['ip'].split('.')
        ip_bytes = struct.pack('!BBBB', int(ip_parts[0]), int(ip_parts[1]), int(ip_parts[2]), int(ip_parts[3]))
        port_bytes = struct.pack('<H', server_entry['port'])
        response_packet += ip_bytes + port_bytes

    def check_filter_criteria(server_entry):
        info_dict = {}
        try:
            parts = server_entry['info'].split('\\')
            for i in range(1, len(parts) - 1, 2):
                info_dict[parts[i]] = parts[i + 1]
        except IndexError:
            return False

        # Check if server matches all filter criteria
        for key, value in filter_info.items():
            if key not in info_dict or info_dict[key] != value:
                return False

        return True

    if ip_filter == b'\x00\x00\x00\x00':
        # Append server IP and port for all matching criteria
        with server_lock:
            for entry in server:
                if entry['lan'] == 0 and entry['proxy'] == 0 and check_filter_criteria(entry):
                    append_server_to_response(entry)
    else:
        # Find the matching IP in the list and append subsequent IPs and ports
        matched = False
        with server_lock:
            for entry in server:
                if entry['ip'] == socket.inet_ntoa(ip_filter):
                    matched = True
                if matched and entry['lan'] == 0 and entry['proxy'] == 0 and check_filter_criteria(entry):
                    append_server_to_response(entry)

    # Send the response packet
    client_socket.sendto(response_packet, client_address)

def handle_getbatchlist(client_socket, request_data):
    # Code for A2S_GETBATCHLIST goes here (as per your previous implementation)
    pass

def handle_getservers(client_socket):
    # Code for handling A2S_GETSERVERS request goes here (as per your previous implementation)
    pass

def handle_shutdown(ip):
    with server_lock:
        for entry in server:
            if entry['ip'] == ip:
                server.remove(entry)
                break

def remove_expired_challenges_loop():
    while True:
        remove_expired_challenges()
        time.sleep(60)

def handle_request(client_socket, request_data, client_address):
    command = ord(request_data[0])
    if command == 0x31:  # A2S_GETCHALLENGE
        handle_getchallenge(client_socket, client_address)
    elif command == 0x42:  # A2S_HEARTBEAT2
        handle_heartbeat2(client_socket, request_data, client_address)
    elif command == 0x43:  # A2S_GETBATCHLIST
        handle_getbatchlist(client_socket, request_data)
    elif command == 0x44:  # A2S_GETBATCHLIST2
        handle_getbatchlist2(client_socket, request_data[1:])
    elif command == 0x64:  # A2S_GETSERVERS
        handle_getservers(client_socket)
    elif command == 0x65:  # A2S_SHUTDOWN
        handle_shutdown(client_address[0])
    elif command == 0x66:  # A2S_GETBATCH
        handle_getbatch(client_socket, request_data[1:])
    else:
        print("Unknown command:", hex(command))

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 27015))

    # Start the challenge expiration thread
    challenge_thread = threading.Thread(target=remove_expired_challenges_loop)
    challenge_thread.daemon = True
    challenge_thread.start()

    print("Server is listening on port 27015...")
    while True:
        data, address = server_socket.recvfrom(4096)
        handle_request(server_socket, data, address)
