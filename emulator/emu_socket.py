import binascii, socket, struct, zlib, os, sys, logging, time
import steam
import utilities

from steamemu.config import read_config
config = read_config()

class ImpSocket :
    "improved socket class - this is REALLY braindead because the socket class doesn't let me override some methods, so I have to build from scratch"
    def __init__(self, sock = None) :
        if sock is None :
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else :
            self.s = sock
        self.start_time = int(time.time())
        self.bytes_sent = 0
        self.bytes_received = 0

            
    def accept(self) :
        (returnedsocket, address) = self.s.accept()
        newsocket = ImpSocket(returnedsocket)
        newsocket.address = address
        return newsocket, address
    

    def bind(self, address) :
        self.address = address
        self.s.bind(address)


    def connect(self, address) :
        self.address = address
        self.s.connect(address)
        logging.debug(str(self.address) + ": Connecting to address")


    def close(self) :
        self.s.close()


    def listen(self, connections) :
        self.s.listen(connections)


    def send(self, data, log = True) :
        sentbytes = self.s.send(data)
        self.bytes_sent += sentbytes
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_sent != 0:
            pass
        else:
            outgoing_kbps = int(self.bytes_sent) / int(elapsed_time) / 1024
        if log :
            logging.debug(str(self.address) + ": Sent data - " + binascii.b2a_hex(data))
        if sentbytes != len(data) :
            logging.warning("NOTICE!!! Number of bytes sent doesn't match what we tried to send " + str(sentbytes) + " " + str(len(data)))
        return sentbytes


    def sendto(self, data, address, log = True) :
        sentbytes = self.s.sendto(data, address)
        self.bytes_sent += sent_bytes
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_sent != 0:
            pass
        else:
            outgoing_kbps = int(self.bytes_sent) / int(elapsed_time) / 1024
        if log :
            logging.debug(str(address) + ": sendto Sent data - " + binascii.b2a_hex(data))
        if sentbytes != len(data) :
            logging.warning("NOTICE!!! Number of bytes sent doesn't match what we tried to send " + str(sentbytes) + " " + str(len(data)))
        return sentbytes


    def send_withlen(self, data, log = True) :
        lengthstr = struct.pack(">L", len(data))
        if log :
            logging.debug(str(self.address) + ": Sent data with length - " + binascii.b2a_hex(lengthstr) + " " + binascii.b2a_hex(data))
        totaldata = lengthstr + data
        totalsent = 0
        while totalsent < len(totaldata) :
            sent = self.send(totaldata, False)
            if sent == 0:
                raise RuntimeError, "socket connection broken"
            totalsent = totalsent + sent


    def recv(self, length, log = True) :
        data = self.s.recv(length)
        self.bytes_received += len(data)
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_received == 0:
            pass
        else:
            incoming_kbps = self.bytes_received / int(elapsed_time) / 1024
        if log :
            logging.debug(str(self.address) + ": Received data - " + binascii.b2a_hex(data))
        return data


    def recvfrom(self, length, log = True) :
        (data, address) = self.s.recvfrom(length)
        self.bytes_received += len(data)
        elapsed_time = int(time.time()) - self.start_time
        if elapsed_time == 0 or self.bytes_received == 0:
            pass
        else:
            incoming_kbps = self.bytes_received / int(elapsed_time) / 1024
        if log :
            logging.debug(str(address) + ": recvfrom Received data - " + binascii.b2a_hex(data))
        return (data, address)


    def recv_all(self, length, log = True) :
        data = ""
        while len(data) < length :
            chunk = self.recv(length - len(data), False)
            if chunk == '':
                raise RuntimeError, "socket connection broken"
            data = data + chunk
        if log :
            logging.debug(str(self.address) + ": Received all data - " + binascii.b2a_hex(data))
        return data

    def recv_withlen(self, log = True) :
        lengthstr = self.recv(4, False)
        if len(lengthstr) != 4 :
            logging.debug("Command header not long enough, should be 4, is " + str(len(lengthstr)))
            return "\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" #DUMMY RETURN FOR FILESERVER
        else :
            length = struct.unpack(">L", lengthstr)[0]
            data = self.recv_all(length, False)
            logging.debug(str(self.address) + ": Received data with length  - " + binascii.b2a_hex(lengthstr) + " " + binascii.b2a_hex(data))
            return data
        
    def get_outgoing_data_rate(self):
        elapsed_time = time.time() - self.start_time
        outgoing_kbps = self.bytes_sent / elapsed_time / 1024
        return outgoing_kbps

    def get_incoming_data_rate(self):
        elapsed_time = time.time() - self.start_time
        incoming_kbps = self.bytes_received / elapsed_time / 1024
        return incoming_kbps
