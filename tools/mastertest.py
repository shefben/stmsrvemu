import random
import socket
import struct
import time

# Constants
MASTER_SERVER_IP = '192.168.3.180'  # Replace with the actual IP of the master server
MASTER_SERVER_PORT = 27010  # Replace with the actual port of the master server
NUM_SERVERS = 100  # Number of servers to simulate


# Function to create a random server info string
def create_random_server_info(challenge):
    protocol = 46
    num_players = random.randint(0, 20)
    max_players = random.randint(num_players, 40)
    bots = random.randint(0, 10)
    gamedir = "valve"
    map_name = "crossfire"
    os_type = random.choice(["l", "w"])
    dedicated = random.randint(0, 1)
    password = random.randint(0, 1)
    secure = random.randint(0, 1)
    lan = random.randint(0, 1)
    version = "1.1.2.7/Stdio"
    info = f"\\protocol\\{protocol}\\challenge\\{challenge}\\players\\{num_players}\\max\\{max_players}" \
           f"\\bots\\{bots}\\gamedir\\{gamedir}\\map\\{map_name}\\os\\{os_type}\\dedicated\\{dedicated}" \
           f"\\password\\{password}\\secure\\{secure}\\lan\\{lan}\\version\\{version}"
    return info


# Create a socket


# Simulate servers
for i in range(NUM_SERVERS):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Send challenge request ('q')
    challenge_request = b'q'
    sock.sendto(challenge_request, (MASTER_SERVER_IP, MASTER_SERVER_PORT))

    # Receive challenge response
    response, _ = sock.recvfrom(1024)
    challenge_value = struct.unpack('<I', response[6:])[0]

    # Create and send heartbeat2 packet ('0')
    server_info = create_random_server_info(challenge_value)
    heartbeat2_packet = b'0' + server_info.encode('iso-8859-1')
    sock.sendto(heartbeat2_packet, (MASTER_SERVER_IP, MASTER_SERVER_PORT))
    sock.close()
    # Wait a bit before sending the next server's info
    time.sleep(1)

# Close the socket