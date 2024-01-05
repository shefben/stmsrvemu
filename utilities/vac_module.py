import io
import os
import struct


class Module:
    Id = 0x12345678
    pattern = [5, 97, 122, -19, 27, -54, 13, -101, 74, -15, 100, -57, -75, -114, -33, -96]
    pattern2 = [32, 7, 19, 97, 3, 69, 23, 114, 10, 45, 72, 12, 74, 18, -87, -75]

    def __init__(self, source):

        if isinstance(source, str):
            with open(source, 'rb') as file:
                self._init_from_file(file)
        elif isinstance(source, io.BufferedReader):
            self._init_from_file(source)
        else:
            raise TypeError("Invalid source type. Must be a file path or a BufferedReader.")

    def _init_from_file(self, file):
        self.Name = file.read(struct.unpack('>H', file.read(2))[0]).decode('latin-1')
        size = struct.unpack('>I', file.read(4))[0]
        self.Header = file.read(size)
        size = struct.unpack('>I', file.read(4))[0]
        self.Data = file.read(size)
        self.Size = size
        self._encode(self.Data, self.Id)

    def write(self):
        directory = os.path.dirname(self.Name)
        if directory:
            os.makedirs(directory, exist_ok = True)
        with open(self.Name, 'wb') as file:
            self._write_to_file(file)

    def _write_to_file(self, file):
        file.write(struct.pack('>H', len(self.Name)) + self.Name.encode('latin-1'))
        file.write(struct.pack('>I', len(self.Header)) + self.Header)
        file.write(struct.pack('>I', len(self.Data)) + self.Data)

    @staticmethod
    def _decode(data, key):
        Module._process_data(data, key, Module.pattern, False)

    @staticmethod
    def _encode(data, key):
        Module._process_data(data, key, Module.pattern, True)

    @staticmethod
    def _process_data(data, key, pattern, encoding):
        inverted_key = ~key
        for i in range(0, len(data), 1024):
            block = data[i:i + 1024]
            for j in range(0, len(block), 4):
                # Processing each byte of the block
                part = list(block[j:j + 4])
                for k in range(4):
                    if encoding:
                        part[k] ^= inverted_key & 0xff
                    else:
                        part[k] ^= key & 0xff
                    inverted_key >>= 8
                    key >>= 8
                # Swapping and pattern XOR
                part[0], part[1], part[2], part[3] = part[3], part[2], part[1], part[0]
                for k in range(4):
                    part[k] ^= pattern[(i + k) & 0xf]
                block[j:j + 4] = bytes(part)
        return bytes(data)

    def compareHeader(self, module):
        if not self.Header or not module.Header or len(self.Header) != len(module.Header) or len(self.Header) < 20:
            return False
        return self.Header[:20] == module.Header[:20]