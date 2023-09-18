import emu_socket, socket

# Create a UDP socket
serversocket = emu_socket.ImpSocket("udp")

# Bind the socket to the desired IP and port
serversocket.bind(("127.0.0.1", 27013))

print "UDP Server Listening on port 27013"

while True:
    # Receive data from clients
    data, client_address = serversocket.recvfrom(1024)  # Adjust buffer size as needed

    # Handle the received data (replace this with your processing logic)
    print "Received data from {}: {}".format(client_address, data)
