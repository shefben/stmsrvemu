import hashlib
import hmac
import io
import struct
import sys

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.Hash import SHA1
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from config import read_config as get_config

config = get_config()

main_key = RSA.construct((# n
        int(config["main_key_n"], 16),

        # e
        0x11,

        # d
        int(config["main_key_e"], 16),))
main_key_sign = RSA.construct((# n
        # 0x86724794f8a0fcb0c129b979e7af2e1e309303a7042503d835708873b1df8a9e307c228b9c0862f8f5dbe6f81579233db8a4fe6ba14551679ad72c01973b5ee4ecf8ca2c21524b125bb06cfa0047e2d202c2a70b7f71ad7d1c3665e557a7387bbc43fe52244e58d91a14c660a84b6ae6fdc857b3f595376a8e484cb6b90cc992f5c57cccb1a1197ee90814186b046968f872b84297dad46ed4119ae0f402803108ad95777615c827de8372487a22902cb288bcbad7bc4a842e03a33bd26e052386cbc088c3932bdd1ec4fee1f734fe5eeec55d51c91e1d9e5eae46cf7aac15b2654af8e6c9443b41e92568cce79c08ab6fa61601e4eed791f0436fdc296bb373L,

        int(config["main_key_n"], 16), # e
        # 0x07e89acc87188755b1027452770a4e01c69f3c733c7aa5df8aac44430a768faef3cb11174569e7b44ab2951da6e90212b0822d1563d6e6abbdd06c0017f46efe684adeb74d4113798cec42a54b4f85d01e47af79259d4670c56c9c950527f443838b876e3e5ef62ae36aa241ebc83376ffde9bbf4aae6cabea407cfbb08848179e466bcb046b0a857d821c5888fcd95b2aae1b92aa64f3a6037295144aa45d0dbebce075023523bce4243ae194258026fc879656560c109ea9547a002db38b89caac90d75758e74c5616ed9816f3ed130ff6926a1597380b6fc98b5eeefc5104502d9bee9da296ca26b32d9094452ab1eb9cf970acabeecde6b1ffae57b56401L,

        int(config["main_key_e"], 16), # d
        0x11,))
network_key = RSA.construct((# n
        # 0xbf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059L,
        int(config["net_key_n"], 16), # e
        0x11, # d
        # 0x4ee3ec697bb34d5e999cb2d3a3f5766210e5ce961de7334b6f7c6361f18682825b2cfa95b8b7894c124ada7ea105ec1eaeb3c5f1d17dfaa55d099a0f5fa366913b171af767fe67fb89f5393efdb69634f74cb41cb7b3501025c4e8fef1ff434307c7200f197b74044e93dbcf50dcc407cbf347b4b817383471cd1de7b5964a9dL,
        int(config["net_key_d"], 16),))
network_key_sign = RSA.construct((# n
        # 0xbf973e24beb372c12bea4494450afaee290987fedae8580057e4f15b93b46185b8daf2d952e24d6f9a23805819578693a846e0b8fcc43c23e1f2bf49e843aff4b8e9af6c5e2e7b9df44e29e3c1c93f166e25e42b8f9109be8ad03438845a3c1925504ecc090aabd49a0fc6783746ff4e9e090aa96f1c8009baf9162b66716059L,
        int(config["net_key_n"], 16), # e
        # 0x4ee3ec697bb34d5e999cb2d3a3f5766210e5ce961de7334b6f7c6361f18682825b2cfa95b8b7894c124ada7ea105ec1eaeb3c5f1d17dfaa55d099a0f5fa366913b171af767fe67fb89f5393efdb69634f74cb41cb7b3501025c4e8fef1ff434307c7200f197b74044e93dbcf50dcc407cbf347b4b817383471cd1de7b5964a9dL,
        int(config["net_key_d"], 16), # d
        0x11,))

BERstring = network_key.public_key().export_key("DER")


def get_aes_key(encryptedstring, rsakey):
    return PKCS1_OAEP.new(rsakey).decrypt(encryptedstring)


def verify_message(key, message):
    key += b"\x00" * 48
    xor_a = b"\x36" * 64
    xor_b = b"\x5c" * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message[:-20]
    checksum_a = SHA1.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA1.new(phrase_b).digest()
    if checksum_b == message[-20:]:
        return True
    else:
        return False


def sign_message(key, message):
    key += b"\x00" * 48
    xor_a = b"\x36" * 64
    xor_b = b"\x5c" * 64
    key_a = binaryxor(key, xor_a)
    key_b = binaryxor(key, xor_b)
    phrase_a = key_a + message
    checksum_a = SHA1.new(phrase_a).digest()
    phrase_b = key_b + checksum_a
    checksum_b = SHA1.new(phrase_b).digest()
    return checksum_b


def rsa_sign_message(rsakey, message):
    signature = pkcs1_15.new(rsakey).sign(SHA1.new(message))
    return signature


def rsa_sign_message_1024(rsakey, message):
    signature = pkcs1_15.new(rsakey).sign(SHA1.new(message))
    return signature


def get_mainkey_reply():
    signature = rsa_sign_message_1024(main_key, BERstring)
    # signature = utils.rsa_sign_message(steam.network_key_sign, BERstring)
    return struct.pack(">H", len(BERstring)) + BERstring + struct.pack(">H", len(signature)) + signature


signed_mainkey_reply = get_mainkey_reply()


def aes_decrypt(key, IV, message):
    decrypted = b""  # Initialize as bytes

    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0

    while i < len(message):
        cipher = message[i:i + 16]

        decrypted += cryptobj.decrypt(cipher)  # Use += to concatenate bytes

        i += 16

    return decrypted


def aes_encrypt(key, IV, message):
    """"# Ensure key, IV, and message are bytes
    key = key.encode('utf-8') if isinstance(key, str) else key
    IV = IV.encode('utf-8') if isinstance(IV, str) else IV
    message = message.encode('utf-8') if isinstance(message, str) else message"""

    # pad the message
    overflow = len(message) % 16
    message += bytes([16 - overflow] * (16 - overflow))

    encrypted = b""

    cryptobj = AES.new(key, AES.MODE_CBC, IV)
    i = 0

    while i < len(message):
        cipher = message[i:i + 16]

        encrypted = encrypted + cryptobj.encrypt(cipher)

        i += 16

    return encrypted


def encrypt_with_pad(key, IV, ptext):
    padsize = 16 - len(ptext) % 16
    ptext += bytes([padsize] * padsize)

    aes = AES.new(key, AES.MODE_CBC, IV)
    ctext = aes.encrypt(ptext)

    return ctext


def encrypt_message(ptext, key):
    IV = bytes.fromhex("92183129534234231231312123123353")
    ctext = encrypt_with_pad(key, IV, ptext)

    return IV + struct.pack(">HH", len(ptext), len(ctext)) + ctext


"""def binaryxor(bytesA, bytesB) :
    if len(bytesA) != len(bytesB) :
        print("binaryxor: byte lengths don't match!!")
        sys.exit( )

    outBytes = bytearray( )
    for i in range(len(bytesA)) :
        valA = bytesA[i]
        valB = bytesB[i]
        valC = valA ^ valB
        outBytes.append(valC)
    return bytes(outBytes)"""


def binaryxor(a, b):
    if len(a) != len(b):
        raise Exception("binaryxor: string lengths doesn't match!!")

    return bytes(aa ^ bb for aa, bb in zip(a, b))


def textxor(textstring):
    key = "@#$%^&*(}]{;:<>?*&^+_-="
    xorded = ""
    j = 0
    for i in range(len(textstring)):
        if j == len(key):
            j = 0
        valA = ord(textstring[i])
        valB = ord(key[j])
        valC = valA ^ valB
        xorded += chr(valC)
        j += 1
    return xorded


def chunk_aes_decrypt(key, chunk):
    cryptobj = AES.new(key, AES.MODE_ECB)
    output = b""
    lastblock = b"\x00" * 16

    for i in range(0, len(chunk), 16):
        block = chunk[i:i + 16]
        block = block.ljust(16)
        key2 = cryptobj.encrypt(lastblock)
        output += binaryxor(block, key2)
        lastblock = block

    return output[:len(chunk)]


def encrypt_with_pad(ptext, key, IV):
    padsize = 16 - len(ptext) % 16
    ptext += bytes([padsize] * padsize)

    aes = AES.new(key, AES.MODE_CBC, IV)
    ctext = aes.encrypt(ptext)

    return ctext


# BASIC xor functions for peer packet 'encryption'
def encrypt(message, password):
    encrypted = ""
    for i in range(len(message)):
        char = message[i]
        key = password[i % len(password)]
        encrypted += chr(ord(char) ^ ord(key))
    return encrypted


def encrypt_bytes(message, password):
    encrypted = bytearray()
    for i in range(len(message)):
        char = message[i]
        key = password[i % len(password)]
        encrypted.append(char ^ ord(key))
    return bytes(encrypted)


# Assuming password is a string and message is bytes


def decrypt(encrypted, password):
    decrypted = ""
    for i in range(len(encrypted)):
        char = encrypted[i]
        key = password[i % len(password)]
        decrypted += chr(ord(char) ^ ord(key))
    return decrypted


def decrypt_bytes(encrypted, password):
    decrypted = bytearray()
    for i in range(len(encrypted)):
        byte = encrypted[i]
        key = password[i % len(password)]
        decrypted.append(byte ^ ord(key))
    return decrypted  # or appropriate encoding


# Beta 1 encryption functions
def beta_encrypt_message(ptext, key):
    IV = bytes.fromhex("92183129534234231231312123123353")
    ctext = encrypt_with_pad(ptext, key, IV)

    return IV + struct.pack(">HH", len(ptext), len(ctext)) + ctext


def decrypt_message(msg, key):
    bio = io.BytesIO(msg)
    IV = bio.read(16)
    ptextsize, ctextsize = struct.unpack(">HH", bio.read(4))
    ctext = bio.read(ctextsize)

    if bio.read() != b"":
        print("extra data at end of message")
        return

    aes = AES.new(key, AES.MODE_CBC, IV)
    ptext = aes.decrypt(ctext)
    print("removing padding at end", ptext[ptextsize:].hex())
    ptext = ptext[:ptextsize]
    return ptext


def beta_decrypt_message_v1(msg, key):
    bio = io.BytesIO(msg)

    # ctextsize is just zero in steam 2002
    ptextsize, ctextsize = struct.unpack("<HH", bio.read(4))
    IV = bio.read(16)

    ctext = bio.read()
    # crop off misaligned data
    ctext = ctext[:len(ctext) & 0xfffffff0]

    if ptextsize + 1 > len(ctext):
        print("badly misaligned data")
        sys.exit()

    aes = AES.new(key, AES.MODE_CBC, IV)
    ptext = aes.decrypt(ctext)
    print("removing padding at end", ptext[ptextsize:].hex())
    ptext = ptext[:ptextsize]
    return ptext


def validate_mac(msg, key):
    if hmac.digest(key, msg[:-20], hashlib.sha1) != msg[-20:]:
        raise Exception("Bad MAC")

    return True