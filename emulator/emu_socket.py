import binascii
import socket
import struct
import time
import logging
import threading


class ImpSocketThread(threading.Thread):
    def __init__(self, imp_socket):
        super(ImpSocketThread, self).__init__()
        self.imp_socket = imp_socket

    def run(self):
        while True:
            self.imp_socket.run_frame()


class ImpSocket:
    def __init__(self, sock=None):
        if sock is None or sock == "tcp":
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        elif sock == "udp":
            self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.s = sock
        self.start_time = int(time.time())
        self.address = 0
        self.port = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.bytes_sent_total = 0
        self.bytes_received_total = 0
        self.start_time_minute = int(time.time())
        self.bytes_sent_minute = 0
        self.bytes_received_minute = 0
        self.log_file = None
        self.log_interval = 300  # 5 minutes
        self.thread = ImpSocketThread(self)

    def start(self):
        self.thread.start()

    def accept(self):
        if isinstance(self.s, socket.socket):
            (returnedsocket, address) = self.s.accept()
            newsocket = ImpSocket(returnedsocket)
            newsocket.address = address
            return newsocket, address
        else:
            raise ValueError("Cannot accept on a non-socket")

    def bind(self, address):
        #if isinstance(self.s, socket.socket):
        self.address = address
        #self.address, self.port = address
        self.s.bind(address)
        #else:
            #raise ValueError("Cannot bind on a non-socket")

    def connect(self, address):
        if isinstance(self.s, socket.socket):
            self.address = address
            self.s.connect(address)
            logging.debug(str(self.address) + ": Connecting to address")
        else:
            raise ValueError("Cannot connect on a non-socket")

    def close(self):
        if isinstance(self.s, socket.socket):
            self.s.close()

    def listen(self, connections):
        if isinstance(self.s, socket.socket):
            self.s.listen(connections)
        else:
            raise ValueError("Cannot listen on a non-socket")

    def send(self, data, log=True):
        sentbytes = self.s.send(data)
        self.bytes_sent += sentbytes
        self.bytes_sent_total += sentbytes
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_sent != 0:
            pass
        else:
            outgoing_kbps = int(self.bytes_sent) / int(elapsed_time) / 1024
        if log:
            logging.debug(
                str(self.address) + ": Sent data - " + binascii.b2a_hex(data))
        if sentbytes != len(data):
            logging.warning(
                "NOTICE!!! Number of bytes sent doesn't match what we tried to send "
                + str(sentbytes) + " " + str(len(data)))
        return sentbytes

    def sendto(self, data, address, log=True):
        sentbytes = self.s.sendto(data, address)
        self.bytes_sent += sentbytes
        self.bytes_sent_total += sentbytes
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_sent != 0:
            pass
        else:
            outgoing_kbps = int(self.bytes_sent) / int(elapsed_time) / 1024
        if log:
            logging.debug(
                str(address) + ": sendto Sent data - " +
                binascii.b2a_hex(data))
        if sentbytes != len(data):
            logging.warning(
                "NOTICE!!! Number of bytes sent doesn't match what we tried to send "
                + str(sentbytes) + " " + str(len(data)))
        return sentbytes

    def send_withlen(self, data, log=True):
        lengthstr = struct.pack(">L", len(data))
        if log:
            logging.debug(
                str(self.address) + ": Sent data with length - " +
                binascii.b2a_hex(lengthstr) + " " + binascii.b2a_hex(data))
        totaldata = lengthstr + data
        totalsent = 0
        while totalsent < len(totaldata):
            sent = self.send(totaldata, False)
            if sent == 0:
                logging.warning("Warning! Connection Lost!")
            totalsent = totalsent + sent

    def recv(self, length, log=True):
        data = self.s.recv(length)
        self.bytes_received += len(data)
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_received == 0:
            pass
        else:
            incoming_kbps = self.bytes_received / int(elapsed_time) / 1024
        if log:
            logging.debug(
                str(self.address) + ": Received data - " +
                binascii.b2a_hex(data))
        return data

    def recvfrom(self, length, log=True):
        data, address = self.s.recvfrom(length)
        self.bytes_received += len(data)
        self.bytes_received_total += len(data)
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_received == 0:
            pass
        else:
            incoming_kbps = self.bytes_received / elapsed_time / 1024
        if log:
            logging.debug(
                str(address) + ": recvfrom Received data - " +
                binascii.b2a_hex(data))
        return (data, address)

    def recv_all(self, length, log=True):
        data = ""
        while len(data) < length:
            chunk = self.recv(length - len(data), False)
            if chunk == '':
                raise RuntimeError("Socket connection broken")
            data = data + chunk
        if log:
            logging.debug(
                str(self.address) + ": Received all data - " +
                binascii.b2a_hex(data))
        return data

    def recv_withlen(self, log=True):
        lengthstr = self.recv(4, False)
        if len(lengthstr) != 4:
            logging.debug("Command header not long enough, should be 4, is " +
                          str(len(lengthstr)))
            return "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # DUMMY RETURN FOR FILESERVER
        else:
            length = struct.unpack(">L", lengthstr)[0]
            data = self.recv_all(length, False)
            logging.debug(
                str(self.address) + ": Received data with length  - " +
                binascii.b2a_hex(lengthstr) + " " + binascii.b2a_hex(data))
            return data

    def get_outgoing_data_rate(self):
        elapsed_time = time.time() - self.start_time
        outgoing_kbps = self.bytes_sent / elapsed_time / 1024
        return outgoing_kbps

    def get_incoming_data_rate(self):
        elapsed_time = time.time() - self.start_time
        incoming_kbps = self.bytes_received / elapsed_time / 1024
        return incoming_kbps

    def get_total_bytes_in(self):
        return self.bytes_received

    def get_total_bytes_out(self):
        return self.bytes_sent
    
    def get_port(self):
        return self.port
    
    def get_ip(self):
        return self.address

    def run_frame(self):
        while True:
            current_time = int(time.time())
            elapsed_time = current_time - self.start_time_minute

            # Create lists of sockets to monitor
            read_sockets = [self.s]  # Monitor this socket for incoming data
            write_sockets = []  # Monitor this socket for outgoing data

            # Use select to block until a socket becomes ready
            readable, writable, _ = select.select(read_sockets, write_sockets, [],
                                                0)

            for sock in readable + writable:
                if elapsed_time >= self.log_interval:
                    # Calculate per-minute data rates
                    outgoing_kbps_minute = (
                        self.bytes_sent - self.bytes_sent_minute) / elapsed_time / 1024
                    incoming_kbps_minute = (
                        self.bytes_received -
                        self.bytes_received_minute) / elapsed_time / 1024

                    # Reset per-minute counters
                    self.start_time_minute = current_time
                    self.bytes_sent_minute = self.bytes_sent
                    self.bytes_received_minute = self.bytes_received

                    # Log statistics to a file
                    #self.log_statistics(outgoing_kbps_minute, incoming_kbps_minute)

            # Add a sleep to avoid high CPU usage when no activity is happening
            time.sleep(0.1)  # Adjust the sleep duration as needed

    def log_statistics(self, outgoing_kbps_minute, incoming_kbps_minute):
        if self.log_file is None:
            log_filename = time.strftime("/logs/networklogs-%m-%d-%y.log")
            self.log_file = open(log_filename, "a")

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = "%s Outgoing (KBps): %.2f, Incoming (KBps): %.2f\n" % (
            timestamp, outgoing_kbps_minute, incoming_kbps_minute)
        self.log_file.write(log_message)
        self.log_file.flush()
