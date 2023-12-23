import binascii
import csv
import datetime
import logging
import os
import os.path
import socket
import struct
import time
import globalvars
import utilities
import utils

from utilities.networkbuffer import NetworkBuffer
from utilities.networkhandler import UDPNetworkHandler
class DataBuffer:
	def __init__(self, data):
		if not isinstance(data, bytes):
			raise TypeError("Data must be a bytes object")
		self.data = data
		self.cursor = 0

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

	def add_packeddata(self, packed_data):
		self.data += packed_data

	def get_data(self):
		return bytes(self.data)

class VAC1Server(UDPNetworkHandler) :


	def __init__(self, port, config) :
		self.server_type = "VAC1Server"
		super(VAC1Server, self).__init__(config, int(port), self.server_type)  # Create an instance of NetworkHandler

	def handle_client(self, data, address):
		log = logging.getLogger(self.server_type)
		clientid = str(address) + ": "
		log.info(clientid + "Connected to Valve Anti-Cheat 1 (2002-2004) Server")
		log.debug(clientid + ("Received message: %s, from %s" % (repr(data), address)))

		data = DataBuffer(data)
		A = data.unpack_int()
		B = data.unpack_byte()
		C = data.unpack_byte()

		data = data[7:]
		if B != 0x77:
			command = data.unpack_string()
		else:
			command = b"CheckAccess"

		if command != b"CHALLENGE": #Check Access / Get SessionID
			isLegal = True if (A == -1 and B == 0x77 and C == 0x00) else False
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
				reply.pack_int(-1)
				reply.pack_byte(0x75)
				reply.pack_byte(0x00)
				reply.pack_bytes(b"ABORT\x00")
				reply.pack_bytes(b"Protocol Error!\x00")

			self.serversocket.sendto(reply, address)
			self.serversocket.close()