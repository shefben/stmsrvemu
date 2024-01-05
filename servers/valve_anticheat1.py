import logging
import os
import os.path
import struct

from utilities.networkhandler import UDPNetworkHandler
from utilities.vac_module import Module


class DataBuffer:
    def __init__(self, data):
        if not isinstance(data, bytes):
            raise TypeError("Data must be a bytes object")
        self.data = data
        self.cursor = 0
        self.A = 0
        self.B = 0
        self.C = 0
        self.command = None

    def unpack_header(self):
        self.A = self.unpack_int()
        self.B = self.unpack_byte()
        self.C = self.unpack_byte()
        if self.B != 0x77:
            self.command = self.unpack_string()[:-1]
        else:
            self.command = b"CheckAccess"

    def unpack_int(self):
        try:
            value = struct.unpack_from('<i', self.data, self.cursor)[0]
            self.cursor += 4
            return value
        except struct.error:
            raise ValueError("Insufficient data for unpacking an int")

    def unpack_short(self):
        try:
            value = struct.unpack_from('<h', self.data, self.cursor)[0]
            self.cursor += 2
            return value
        except struct.error:
            raise ValueError("Insufficient data for unpacking a short")

    def unpack_byte(self):
        try:
            value = struct.unpack_from('B', self.data, self.cursor)[0]
            self.cursor += 1
            return value
        except struct.error:
            raise ValueError("Insufficient data for unpacking a byte")

    def unpack_bytes(self, length):
        if self.cursor + length > len(self.data):
            raise ValueError("Insufficient data for unpacking bytes")
        value = struct.unpack_from(f'{length}s', self.data, self.cursor)[0]
        self.cursor += length
        return value

    def unpack_string(self):
        end = self.data.find(b'\x00', self.cursor)
        if end == -1:
            raise ValueError("Null terminator not found in string data")
        string_data = self.data[self.cursor:end]
        self.cursor = end + 1
        return string_data.decode('latin-1')


class DataBufferBuilder:
    def __init__(self):
        self.data = bytearray()

    def pack_int(self, i):
        self.data += struct.pack('<i', i)

    def pack_short(self, i):
        self.data += struct.pack('<h', i)

    def pack_byte(self, i):
        self.data += struct.pack('B', i)

    def pack_bytes(self, data):
        self.data += struct.pack(f'{len(data)}s', data)

    def pack_string(self, string):
        encoded_string = string.encode('latin-1') + b'\x00'
        self.pack_bytes(encoded_string)

    def get_data(self):
        return bytes(self.data)


class VAC1Server(UDPNetworkHandler):

    def __init__(self, port, config):
        self.server_type = "VAC1Server"
        super(VAC1Server, self).__init__(config, int(port), self.server_type)  # Create an instance of NetworkHandler

    def abort_reply(self, errorstr):
        reply = DataBufferBuilder()
        reply.pack_int(-1)
        reply.pack_byte(0x75)
        reply.pack_byte(0x00)
        reply.pack_bytes(b"ABORT\x00")
        reply.pack_bytes(errorstr + b"\x00")
        return reply

    def handle_client(self, data, address):
        log = logging.getLogger(self.server_type)
        clientid = str(address) + ": "
        log.info(clientid + "Connected to Valve Anti-Cheat 1 (2002-2004) Server")
        log.debug(clientid + ("Received message: %s, from %s" % (repr(data), address)))

        data = DataBuffer(data)
        data.unpack_header()
        if data.command != b"CHALLENGE":  # Check Access / Get SessionID
            isLegal = True if (data.A == -1 and data.B == 0x77 and data.C == 0x00) else False
            reply = DataBufferBuilder()
            if isLegal:
                sessionID = data.unpack_int()
                reply.pack_int(-1)
                reply.pack_byte(0x78)
                reply.pack_byte(0x00)
                reply.pack_int(sessionID)
                reply.pack_byte(0x01)
                reply.pack_bytes(b"\x00\x00\x00\x00\x00")
            else:
                log.error(f"{clientid} Protocol Error, Incorrect Packet Format!")
                reply = self.abort_reply(b"Protocol Error!")

            self.serversocket.sendto(reply.get_data(), address)  # self.serversocket.close()

        # Send client that we accept their connection request
        reply = DataBufferBuilder()
        reply.pack_int(-1)
        reply.pack_byte(0x75)
        reply.pack_byte(0x00)
        reply.pack_bytes(b"ACCEPT\x00")
        reply.pack_int(Module.Id)
        self.serversocket.sendto(reply.get_data(), address)

        data = DataBuffer(self.serversocket.recv(256))
        data.unpack_header()
        if data.command == b"GET":
            moduleID = data.unpack_int()
            filename = data.unpack_string()
            D = data.unpack_int()
            testdir = data.unpack_string()
            R = []
            R[0] = data.unpack_int()
            R[1] = data.unpack_int()
            R[2] = data.unpack_int()

            if not moduleID == Module.Id:
                log.error(f"{clientid}Requested Module ID Does Not Match Modules Available!")
                reply = self.abort_reply(b"Protocol Error!")
                self.serversocket.sendto(reply.get_data(), address)
                self.serversocket.close()
                return

            log.info(f"{clientid}Requested Module: {filename}")
            filename = f"files/vacmodules/{filename}"
            if not os.path.isfile(filename):
                log.error(f"{clientid}Requested Module Does Not Exist!!")
                reply = self.abort_reply(b"Requested Module Does Not Exist!")
                self.serversocket.sendto(reply.get_data(), address)
                self.serversocket.close()
                return

            reply = DataBufferBuilder()
            vacmodule = Module(filename)

            reply.pack_int(-1)
            reply.pack_byte(0x75)
            reply.pack_byte(0x00)
            reply.pack_bytes(b"FILE\x00")
            reply.pack_int(vacmodule.Size)
            reply.pack_bytes(vacmodule.Header)
            self.serversocket.sendto(reply.get_data(), address)

            while True:
                data = DataBuffer(self.serversocket.recv(256))
                data.unpack_header()

                if data.command == b"ABORT":
                    log.info(f"{clientid}Connection Closed")
                    break
                elif data.command != b"NEXT":
                    log.info(f"{clientid}Expected 'NEXT' But Recieved: {data.command}")
                    reply = self.abort_reply(b"Expected NEXT Chunk Packet!")
                    self.serversocket.sendto(reply.get_data(), address)
                    break

                filepos = data.unpack_int()

                if filepos < 0 or filepos > vacmodule.Size:
                    log.error(f"{clientid}Invalid 'Next' Chunk packet format!")
                    reply = self.abort_reply(b"Invalid Next Chunk Request Packet Format!")
                    self.serversocket.sendto(reply.get_data(), address)
                    break

                reply = DataBufferBuilder()

                if filepos == vacmodule.Size:
                    reply.pack_int(-1)
                    reply.pack_byte(0x75)
                    reply.pack_byte(0x00)
                    reply.pack_bytes(b"FINISH\x00")
                    self.serversocket.sendto(reply.get_data(), address)
                    log.info(f"{clientid}Completed Sending Module!")
                    break

                # Calculate the size of the data block to send
                data_block_size = min(1024, vacmodule.Size - filepos)

                # Extract the data block
                data_block = vacmodule.Data[filepos:filepos + data_block_size]

                # Pack and send the data block
                reply.pack_int(-1)
                reply.pack_byte(0x75)
                reply.pack_byte(0x00)
                reply.pack_bytes(b"BLOCK\x00")
                reply.pack_short(len(data_block))
                reply.pack_bytes(data_block)
                self.serversocket.sendto(reply.get_data(), address)

            self.serversocket.close()
        log.info(f"{clientid}Disconnected")