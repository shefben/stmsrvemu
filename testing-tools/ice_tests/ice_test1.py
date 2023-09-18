from CryptICE import IceKey

data = 'Hello, World!'
key = bytearray([0x25, 0x6C, 0xC7, 0x0A, 0x00, 0x30, 0x00, 0x5C])

ice = IceKey(1, key)

encrypted_data = ice.Encrypt(data, True)
print('Encrypted =', encrypted_data)  # The output format might vary depending on the library
print('Decrypted =', ice.Decrypt(encrypted_data).rstrip('\x03'))  # Remove padding characters
print('Decrypted =', ice.Decrypt(encrypted_data, True))  # No need to remove padding here
