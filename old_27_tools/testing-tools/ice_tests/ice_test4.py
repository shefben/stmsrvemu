import ctypes
import binascii

# Load the shared library or DLL
cser_decrypt_lib = ctypes.CDLL('ice_key.dll')  # Replace 'your_library_name.dll' with the actual library name

# Specify argument types and return type for the C function
cser_decrypt_lib.cser_decrypt.argtypes = [ctypes.c_char_p]  # Argument is a pointer to char
cser_decrypt_lib.cser_decrypt.restype = ctypes.POINTER(ctypes.c_ubyte)  # Return type is a pointer to unsigned char

# Define a Python wrapper function
def cser_decrypt(data):
    # Call the C function and return the result as a Python bytes object
    result = cser_decrypt_lib.cser_decrypt(data)
    return result

# Example usage
if __name__ == "__main__":
    # Encrypt a plaintext (hexadecimal string)
    plaintext_hex = '670a01a800e53115db3f1d4b5a7d0cc433f3635c2afe3fabf913e17832a77a6634e6869d1890f94d6c07a040c1da658c0db05d52abdc9ea0a43c5309818ddd7aa26e75f66a64a8fe08c16fb485c2d0a441f818c2aff8985a0f420a327b255f3654820e9ed29bf7c2d3d15b2b8d9ba66b14de56064a82a89d660b4f728ae4cb95424f095b539408330c5f44e49ca95b0fe289512e6206a05f2a564b35d0cc429569caef513fae95b2e8dedffde2'
    
    # Convert the hexadecimal string to bytes
    plaintext = binascii.unhexlify(plaintext_hex)

    decrypted_data = cser_decrypt(plaintext)
    
    # Determine the length of the decrypted data
    decrypted_length = len(plaintext)
    
    # Slice the decrypted data based on its length
    decrypted_bytes = bytes(decrypted_data[:decrypted_length])
    
    # Print the decrypted data as raw binary
    print('Decrypted Data:', decrypted_bytes)
