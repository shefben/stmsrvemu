import ctypes
import os
import struct
from ctypes import *
# Determine the bitness of the Python interpreter
is_64_bit = struct.calcsize("P") * 8 == 64

# Load the DLL based on the bitness
dll_name = "ice_key.32.dll" if not is_64_bit else "ice_key.dll"
dll_path = os.path.abspath(dll_name)

ice_dll = ctypes.cdll.LoadLibrary(dll_path)

# Set the key
key = str(b'\x1B\xC8\x0D\x0E\x53\x2D\xB8\x36')  # Replace with your key

# Encrypt a plaintext
plaintext = '670a01a800e53115db3f1d4b5a7d0cc433f3635c2afe3fabf913e17832a77a6634e6869d1890f94d6c07a040c1da658c0db05d52abdc9ea0a43c5309818ddd7aa26e75f66a64a8fe08c16fb485c2d0a441f818c2aff8985a0f420a327b255f3654820e9ed29bf7c2d3d15b2b8d9ba66b14de56064a82a89d660b4f728ae4cb95424f095b539408330c5f44e49ca95b0fe289512e6206a05f2a564b35d0cc429569caef513fae95b2e8dedffde2'

p_test = create_string_buffer(plaintext, len(plaintext))
decrypter = ice_dll.cser_decrypt(plaintext, key)

# Convert the result to a string
decrypted_text = ctypes.string_at(decrypter)

# Print the results
print('Plaintext: %s' % plaintext)
print('Decrypted Text:', str(decrypted_text))

# Print the binary string
print(decrypted_text)

