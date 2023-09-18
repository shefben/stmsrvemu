sMod = [
    [333, 313, 505, 369],
    [379, 375, 319, 391],
    [361, 445, 451, 397],
    [397, 425, 395, 505]
]

sXor = [
    [0x83, 0x85, 0x9b, 0xcd],
    [0xcc, 0xa7, 0xad, 0x41],
    [0x4b, 0x2e, 0xd4, 0x33],
    [0xea, 0xcb, 0x2e, 0x04]
]

pBox = [
    0x00000001, 0x00000080, 0x00000400, 0x00002000,
    0x00080000, 0x00200000, 0x01000000, 0x40000000,
    0x00000008, 0x00000020, 0x00000100, 0x00004000,
    0x00010000, 0x00800000, 0x04000000, 0x20000000,
    0x00000004, 0x00000010, 0x00000200, 0x00008000,
    0x00020000, 0x00400000, 0x08000000, 0x10000000,
    0x00000002, 0x00000040, 0x00000800, 0x00001000,
    0x00040000, 0x00100000, 0x02000000, 0x80000000
]

keyrot = [
    0, 1, 2, 3, 2, 1, 3, 0,
    1, 3, 2, 0, 3, 1, 0, 2
]

class IceKey:

    def __init__(self, level):
        self.size = 0
        self.rounds = 0
        self.keySchedule = []

        if not hasattr(IceKey, "spBox"):
            IceKey.spBox = None
            IceKey.spBoxInitialised = False
            IceKey.spBoxInit()

        if level < 1:
            self.size = 1
            self.rounds = 8
        else:
            self.size = level
            self.rounds = level * 16

        for i in range(self.rounds):
            self.keySchedule.append([0] * 3)

    @staticmethod
    def gf_mult(a, b, m):
        res = 0

        while b != 0:
            if b & 1:
                res ^= a

            a <<= 1
            b >>= 1

            if a >= 256:
                a ^= m

        return res

    @staticmethod
    def gf_exp7(b, m):
        x = 0

        if b == 0:
            return 0

        x = IceKey.gf_mult(b, b, m)
        x = IceKey.gf_mult(b, x, m)
        x = IceKey.gf_mult(x, x, m)
        return IceKey.gf_mult(b, x, m)

    @staticmethod
    def perm32(x):
        res = 0
        i = 0

        while x != 0:
            if x & 1:
                res |= pBox[i]
            i += 1
            x >>= 1

        return res

    @staticmethod
    def spBoxInit():
        IceKey.spBox = []

        for i in range(4):
            col = (i >> 1) & 0xff
            row = (i & 0x1) | ((i & 0x200) >> 8)
            spBoxRow = []

            for j in range(1024):
                x = IceKey.gf_exp7(col ^ sXor[0][row], sMod[0][row]) << 24
                spBoxRow.append(IceKey.perm32(x))

                x = IceKey.gf_exp7(col ^ sXor[1][row], sMod[1][row]) << 16
                spBoxRow.append(IceKey.perm32(x))

                x = IceKey.gf_exp7(col ^ sXor[2][row], sMod[2][row]) << 8
                spBoxRow.append(IceKey.perm32(x))

                x = IceKey.gf_exp7(col ^ sXor[3][row], sMod[3][row])
                spBoxRow.append(IceKey.perm32(x))

            IceKey.spBox.append(spBoxRow)

        IceKey.spBoxInitialised = True

    def scheduleBuild(self, kb, n, krot_idx):
        for i in range(8):
            kr = keyrot[krot_idx + i]
            subkey = self.keySchedule[n + i]
            for j in range(3):
                subkey[j] = 0

            for j in range(15):
                curr_sk = j % 3

                for k in range(4):
                    curr_kb = kb[(kr + k) & 3]
                    bit = curr_kb & 1
                    subkey[curr_sk] = (subkey[curr_sk] << 1) | bit
                    kb[(kr + k) & 3] = (curr_kb >> 1) | ((bit ^ 1) << 15)

    def set(self, key):
        kb = [0] * 4

        if self.rounds == 8:
            for i in range(4):
                kb[3 - i] = (ord(key[i * 2]) << 8) | ord(key[i * 2 + 1])

            self.scheduleBuild(kb, 0, 0)
            return

        for i in range(self.size):
            for j in range(4):
                kb[3 - j] = (ord(key[i * 8 + j * 2]) << 8) | ord(key[i * 8 + j * 2 + 1])

            self.scheduleBuild(kb, i * 8, 0)
            self.scheduleBuild(kb, self.rounds - 8 - i * 8, 8)

    def clear(self):
        for i in range(self.rounds):
            for j in range(3):
                self.keySchedule[i][j] = 0

    def roundFunc(self, p, subkey):
        tl = ((p >> 16) & 0x3ff) | (((p >> 14) | (p << 18)) & 0xffc00)
        tr = (p & 0x3ff) | ((p << 2) & 0xffc00)

        al = subkey[2] & (tl ^ tr)
        ar = al ^ tr
        al ^= tl

        al ^= subkey[0]
        ar ^= subkey[1]

        return IceKey.spBox[0][al >> 10] | IceKey.spBox[1][al & 0x3ff] | \
               IceKey.spBox[2][ar >> 10] | IceKey.spBox[3][ar & 0x3ff]

    def encrypt(self, plaintext, ciphertext):
        l = 0
        r = 0

        for i in range(4):
            l |= (ord(plaintext[i]) & 0xff) << (24 - i * 8)
            r |= (ord(plaintext[i + 4]) & 0xff) << (24 - i * 8)

        for i in range(0, self.rounds, 2):
            l ^= self.roundFunc(r, self.keySchedule[i])
            r ^= self.roundFunc(l, self.keySchedule[i + 1])

        for i in range(4):
            ciphertext[3 - i] = chr(r & 0xff)
            ciphertext[7 - i] = chr(l & 0xff)

            r >>= 8
            l >>= 8

    def decrypt(self, ciphertext, plaintext):
        l = 0
        r = 0

        for i in range(4):
            l |= (ciphertext[i] & 0xFF) << (24 - i * 8)
            r |= (ciphertext[i + 4] & 0xFF) << (24 - i * 8)

        for i in range(self.rounds - 1, 0, -2):
            l ^= self.roundFunc(r, self.keySchedule[i])
            r ^= self.roundFunc(l, self.keySchedule[i - 1])

        for i in range(4):
            plaintext[3 - i] = (r >> (i * 8)) & 0xFF
            plaintext[7 - i] = (l >> (i * 8)) & 0xFF


    def keySize(self):
        return self.size * 8

    def blockSize(self):
        return 8

# Example usage
def split_into_chunks(data, chunk_size):
    chunks = []
    for i in range(0, len(data), chunk_size):
        chunk = data[i:i + chunk_size]
        if len(chunk) < chunk_size:
            chunk += '\x00' * (chunk_size - len(chunk))  # Adding zero padding
        chunks.append(chunk)
    return chunks

def encrypt_data(ice, data):
    encrypted_chunks = []
    for chunk in data:
        encrypted_chunk = bytearray(len(chunk))
        ice.encrypt(chunk, encrypted_chunk)
        encrypted_chunks.append(encrypted_chunk)
    return encrypted_chunks

def decrypt_data(ice, encrypted_data):
    decrypted_chunks = []
    for encrypted_chunk in encrypted_data:
        decrypted_chunk = bytearray(len(encrypted_chunk))
        ice.decrypt(encrypted_chunk, decrypted_chunk)
        decrypted_chunks.append(decrypted_chunk)
    return decrypted_chunks