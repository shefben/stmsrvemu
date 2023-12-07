import logging
import threading
import time

import globalvars
import utilities.socket as emu_socket
from listmanagers import dirlistmanager
from listmanagers.serverlist_utilities import send_heartbeat

# Global variables to track incoming and outgoing data size
incoming_data_size = 0
outgoing_data_size = 0

log = logging.getLogger("NetHandler")


class NetworkHandler(threading.Thread):

    # global manager
    def __init__(self, in_socket, in_config, port, server_type=""):

        threading.Thread.__init__(self)
        self.socket = in_socket
        self.config = in_config
        self.port = port
        if (server_type == "masterdirserver") or server_type == "":
            pass
        else:
            self.server_type = server_type
            if globalvars.public_ip == "0.0.0.0":
                server_ip = globalvars.server_ip_b
            else:
                server_ip = globalvars.public_ip_b
            self.server_info = {
                'wan_ip' : server_ip,
                'lan_ip' : globalvars.server_ip_b,
                'port': int(self.port),
                'server_type': self.server_type,
                'timestamp': int(time.time())
            }
            if not globalvars.aio_server:
                self.start_heartbeat_thread()
            else:
                addserver = dirlistmanager.manager.add_server_info(server_ip, globalvars.server_ip_b, int(self.port), self.server_type, 1)
                if addserver != -1:
                    log.info("Server Added to Directory Server List: " + self.server_type)
                else:
                    log.error("Server Not added to list! Please contact support.")
                    return

    def start_heartbeat_thread(self):
        thread2 = threading.Thread(target=self.heartbeat_thread)
        thread2.daemon = True
        thread2.start()

    def heartbeat_thread(self):
        while True:
            send_heartbeat(self.server_info)
            time.sleep(1800)  # 30 minutes

    def calculate_data_rates(self):
        outgoing = self.socket.get_outgoing_data_rate()
        incoming = self.socket.get_incoming_data_rate()
        return incoming, outgoing
        # print(f"Outgoing data rate: {outgoing_kbps:.2f} KB/s")
        # print(f"Incoming data rate: {incoming_kbps:.2f} KB/s")

    def start_monitoring(self):
        monitor_thread = threading.Thread(target=self.calculate_data_rates)
        monitor_thread.daemon = True  # Thread will exit when main program ends
        monitor_thread.start()

    def handle_client(self):

        raise NotImplementedError("handle_client method must be implemented in derived classes")


class TCPNetworkHandler(NetworkHandler):
    def __init__(self, in_config, port, server_type=""):
        self.serversocket = emu_socket.ImpSocket()
        NetworkHandler.__init__(self, self.serversocket, in_config, port, server_type)
        self.port = port
        self.config = in_config
        self.address = None

    def run(self):
        self.serversocket.bind((globalvars.server_ip, int(self.port)))
        self.serversocket.listen(5)

        while True:
            client_socket, client_address = self.serversocket.accept()
            server_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            server_thread.start( )

    def handle_client(self, client_socket, client_address):
        raise NotImplementedError("handle_client method must be implemented in derived classes")


class UDPNetworkHandler(NetworkHandler):
    def __init__(self, in_config, port, server_type=""):
        self.serversocket = emu_socket.ImpSocket("udp")
        NetworkHandler.__init__(self, self.serversocket, in_config, port, server_type)
        self.port = port
        self.config = in_config

    def run(self):
        self.serversocket.bind((globalvars.server_ip, int(self.port)))
        while True:
            data, address = self.serversocket.recvfrom(2048)
            server_thread = threading.Thread(target=self.handle_client, args=(data, address)).start()

    def handle_client(self, data, address):
        raise NotImplementedError("handle_client method must be implemented in derived classes")


class TCPUDPNetworkHandler(TCPNetworkHandler, UDPNetworkHandler):
    def __init__(self, in_config, port, server_type=""):
        TCPNetworkHandler.__init__(self, in_config, port, server_type)
        UDPNetworkHandler.__init__(self, in_config, port, server_type)


""" # Example handle_client function; for accepting/handling both UDP and TCP Connections
    def handle_client(self):
        try:
            while True:
                if isinstance(self.socket, emu_socket.ImpSocket):  # Check if it's TCP
                    (client_socket, self.address) = self.socket.accept()
                    print("Received a TCP connection from", self.address)
                    # Handle TCP connection
                    # Add your TCP handling code here
                elif isinstance(self.socket, emu_socket.ImpUDPSocket):  # Check if it's UDP
                    data, self.address = self.socket.recvfrom(2048)
                    print("Received a UDP message from", self.address)
                    # Handle UDP connection
                    # Add your UDP handling code here
                else:
                    # Unknown socket type
                    print("Received an unknown socket type from", self.address)
        except KeyboardInterrupt:
            pass
"""