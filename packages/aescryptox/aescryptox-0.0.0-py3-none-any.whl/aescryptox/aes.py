from .utils import pad, unpad
from .modes import AESMode

Nb = 4  # Block size (columns)

# === S-Boxes ===
S_BOX = [
    0x63,0x7C,0x77,0x7B,0xF2,0x6B,0x6F,0xC5,0x30,0x01,0x67,0x2B,0xFE,0xD7,0xAB,0x76,
    0xCA,0x82,0xC9,0x7D,0xFA,0x59,0x47,0xF0,0xAD,0xD4,0xA2,0xAF,0x9C,0xA4,0x72,0xC0,
    0xB7,0xFD,0x93,0x26,0x36,0x3F,0xF7,0xCC,0x34,0xA5,0xE5,0xF1,0x71,0xD8,0x31,0x15,
    0x04,0xC7,0x23,0xC3,0x18,0x96,0x05,0x9A,0x07,0x12,0x80,0xE2,0xEB,0x27,0xB2,0x75,
    0x09,0x83,0x2C,0x1A,0x1B,0x6E,0x5A,0xA0,0x52,0x3B,0xD6,0xB3,0x29,0xE3,0x2F,0x84,
    0x53,0xD1,0x00,0xED,0x20,0xFC,0xB1,0x5B,0x6A,0xCB,0xBE,0x39,0x4A,0x4C,0x58,0xCF,
    0xD0,0xEF,0xAA,0xFB,0x43,0x4D,0x33,0x85,0x45,0xF9,0x02,0x7F,0x50,0x3C,0x9F,0xA8,
    0x51,0xA3,0x40,0x8F,0x92,0x9D,0x38,0xF5,0xBC,0xB6,0xDA,0x21,0x10,0xFF,0xF3,0xD2,
    0xCD,0x0C,0x13,0xEC,0x5F,0x97,0x44,0x17,0xC4,0xA7,0x7E,0x3D,0x64,0x5D,0x19,0x73,
    0x60,0x81,0x4F,0xDC,0x22,0x2A,0x90,0x88,0x46,0xEE,0xB8,0x14,0xDE,0x5E,0x0B,0xDB,
    0xE0,0x32,0x3A,0x0A,0x49,0x06,0x24,0x5C,0xC2,0xD3,0xAC,0x62,0x91,0x95,0xE4,0x79,
    0xE7,0xC8,0x37,0x6D,0x8D,0xD5,0x4E,0xA9,0x6C,0x56,0xF4,0xEA,0x65,0x7A,0xAE,0x08,
    0xBA,0x78,0x25,0x2E,0x1C,0xA6,0xB4,0xC6,0xE8,0xDD,0x74,0x1F,0x4B,0xBD,0x8B,0x8A,
    0x70,0x3E,0xB5,0x66,0x48,0x03,0xF6,0x0E,0x61,0x35,0x57,0xB9,0x86,0xC1,0x1D,0x9E,
    0xE1,0xF8,0x98,0x11,0x69,0xD9,0x8E,0x94,0x9B,0x1E,0x87,0xE9,0xCE,0x55,0x28,0xDF,
    0x8C,0xA1,0x89,0x0D,0xBF,0xE6,0x42,0x68,0x41,0x99,0x2D,0x0F,0xB0,0x54,0xBB,0x16
]

INV_S_BOX = [0]*256
for i in range(256):
    INV_S_BOX[S_BOX[i]] = i

RCON = [
    0x01000000,0x02000000,0x04000000,0x08000000,0x10000000,
    0x20000000,0x40000000,0x80000000,0x1B000000,0x36000000
]

# Galois field multiplication (8-bit)
def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi_bit = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit:
            a ^= 0x1B
        b >>= 1
    return p


class AES:
    def __init__(self, key: bytes, mode=AESMode.ECB, iv: bytes = None):
        if len(key) not in (16, 24, 32, 32, 64):
            raise ValueError("Key must be 16, 24, 32, or 64 bytes (for XTS).")
        self.key = key
        self.mode = mode
        self.iv = iv or bytes(16)
        if self.mode == AESMode.XTS and len(key) not in (32, 64):
            raise ValueError("XTS mode requires 32 bytes (AES-128-XTS) or 64 bytes (AES-256-XTS) key.")
        if self.mode != AESMode.XTS:
            self.Nk = len(key)//4
            self.Nr = self.Nk + 6
            self.round_keys = self.key_expansion()
        else:
            half = len(key)//2
            self.key1 = key[:half]
            self.key2 = key[half:]
            self.aes1 = AES(self.key1, AESMode.ECB)
            self.aes2 = AES(self.key2, AESMode.ECB)

    # === Key expansion ===
    def key_expansion(self):
        def sub_word(w):
            return ((S_BOX[(w >> 24) & 0xFF] << 24) |
                    (S_BOX[(w >> 16) & 0xFF] << 16) |
                    (S_BOX[(w >> 8) & 0xFF] << 8) |
                    (S_BOX[w & 0xFF]))
        def rot_word(w):
            return ((w << 8) | (w >> 24)) & 0xFFFFFFFF
        w = [0]*(Nb*(self.Nr+1))
        for i in range(self.Nk):
            w[i] = int.from_bytes(self.key[4*i:4*i+4], "big")
        for i in range(self.Nk, Nb*(self.Nr+1)):
            temp = w[i-1]
            if i % self.Nk == 0:
                temp = sub_word(rot_word(temp)) ^ RCON[(i//self.Nk)-1]
            elif self.Nk > 6 and i % self.Nk == 4:
                temp = sub_word(temp)
            w[i] = w[i-self.Nk] ^ temp
        return [w[i:i+4] for i in range(0, len(w), 4)]

    # === Core AES transformations ===
    def sub_bytes(self, s):
        for r in range(4):
            for c in range(4):
                s[r][c] = S_BOX[s[r][c]]

    def inv_sub_bytes(self, s):
        for r in range(4):
            for c in range(4):
                s[r][c] = INV_S_BOX[s[r][c]]

    def shift_rows(self, s):
        s[1] = s[1][1:] + s[1][:1]
        s[2] = s[2][2:] + s[2][:2]
        s[3] = s[3][3:] + s[3][:3]

    def inv_shift_rows(self, s):
        s[1] = s[1][-1:] + s[1][:-1]
        s[2] = s[2][-2:] + s[2][:-2]
        s[3] = s[3][-3:] + s[3][:-3]

    def mix_columns(self, s):
        for c in range(4):
            a = [s[r][c] for r in range(4)]
            s[0][c] = gmul(a[0],2)^gmul(a[1],3)^a[2]^a[3]
            s[1][c] = a[0]^gmul(a[1],2)^gmul(a[2],3)^a[3]
            s[2][c] = a[0]^a[1]^gmul(a[2],2)^gmul(a[3],3)
            s[3][c] = gmul(a[0],3)^a[1]^a[2]^gmul(a[3],2)

    def inv_mix_columns(self, s):
        for c in range(4):
            a = [s[r][c] for r in range(4)]
            s[0][c] = gmul(a[0],14)^gmul(a[1],11)^gmul(a[2],13)^gmul(a[3],9)
            s[1][c] = gmul(a[0],9)^gmul(a[1],14)^gmul(a[2],11)^gmul(a[3],13)
            s[2][c] = gmul(a[0],13)^gmul(a[1],9)^gmul(a[2],14)^gmul(a[3],11)
            s[3][c] = gmul(a[0],11)^gmul(a[1],13)^gmul(a[2],9)^gmul(a[3],14)

    def add_round_key(self, s, rk):
        for c in range(4):
            k = rk[c]
            s[0][c]^=(k>>24)&0xFF
            s[1][c]^=(k>>16)&0xFF
            s[2][c]^=(k>>8)&0xFF
            s[3][c]^=k&0xFF

    # === Encrypt/decrypt block ===
    def encrypt_block(self, block):
        s = [[block[r+4*c] for c in range(4)] for r in range(4)]
        self.add_round_key(s, self.round_keys[0])
        for rnd in range(1, self.Nr):
            self.sub_bytes(s)
            self.shift_rows(s)
            self.mix_columns(s)
            self.add_round_key(s, self.round_keys[rnd])
        self.sub_bytes(s)
        self.shift_rows(s)
        self.add_round_key(s, self.round_keys[self.Nr])
        return bytes(s[r][c] for c in range(4) for r in range(4))

    def decrypt_block(self, block):
        s = [[block[r+4*c] for c in range(4)] for r in range(4)]
        self.add_round_key(s, self.round_keys[self.Nr])
        for rnd in range(self.Nr-1,0,-1):
            self.inv_shift_rows(s)
            self.inv_sub_bytes(s)
            self.add_round_key(s, self.round_keys[rnd])
            self.inv_mix_columns(s)
        self.inv_shift_rows(s)
        self.inv_sub_bytes(s)
        self.add_round_key(s, self.round_keys[0])
        return bytes(s[r][c] for c in range(4) for r in range(4))

    # === ECB/CBC/CTR ===
    def encrypt(self,data:bytes)->bytes:
        if self.mode in (AESMode.GCM, AESMode.XTS):
            raise ValueError("Use dedicated encryptor for this mode.")
        data=pad(data)
        out=b""
        prev=self.iv
        for i in range(0,len(data),16):
            block=data[i:i+16]
            if self.mode==AESMode.CBC:
                block=bytes(a^b for a,b in zip(block,prev))
            enc=self.encrypt_block(block)
            out+=enc
            prev=enc if self.mode==AESMode.CBC else prev
        return out

    def decrypt(self,data:bytes)->bytes:
        if self.mode in (AESMode.GCM, AESMode.XTS):
            raise ValueError("Use dedicated decryptor for this mode.")
        out=b""
        prev=self.iv
        for i in range(0,len(data),16):
            block=data[i:i+16]
            dec=self.decrypt_block(block)
            if self.mode==AESMode.CBC:
                dec=bytes(a^b for a,b in zip(dec,prev))
                prev=block
            out+=dec
        return unpad(out)

    def ctr_encrypt(self,data:bytes)->bytes:
        out=b""
        nonce=bytearray(self.iv)
        for i in range(0,len(data),16):
            keystream=self.encrypt_block(nonce)
            block=data[i:i+16]
            enc=bytes(a^b for a,b in zip(block,keystream))
            out+=enc
            for j in range(15,-1,-1):
                nonce[j]=(nonce[j]+1)&0xFF
                if nonce[j]!=0:break
        return out

    def ctr_decrypt(self,data:bytes)->bytes:
        return self.ctr_encrypt(data)

    # === Galois multiplication (128-bit for GCM) ===
    @staticmethod
    def galois_mult(a: bytes, b: bytes) -> bytes:
        a_int = int.from_bytes(a, 'big')
        b_int = int.from_bytes(b, 'big')
        R = 0xE1000000000000000000000000000000
        res = 0
        for i in range(128):
            if (b_int >> (127 - i)) & 1:
                res ^= a_int
            if a_int & 1:
                a_int = (a_int >> 1) ^ R
            else:
                a_int >>= 1
        return res.to_bytes(16, 'big')

    @classmethod
    def ghash(cls, H: bytes, data: bytes) -> bytes:
        Y = b"\x00" * 16
        for i in range(0, len(data), 16):
            block = data[i:i+16].ljust(16, b"\x00")
            Y = cls.galois_mult(bytes(a ^ b for a, b in zip(Y, block)), H)
        return Y

    # === AES-GCM ===
    def gcm_encrypt(self, data: bytes, aad: bytes = b"") -> tuple:
        H = self.encrypt_block(b"\x00" * 16)
        ciphertext = self.ctr_encrypt(data)
        len_block = (len(aad)*8).to_bytes(8, 'big') + (len(data)*8).to_bytes(8, 'big')
        auth_data = aad + b"\x00"*((16 - len(aad)%16)%16)
        cipher_padded = ciphertext + b"\x00"*((16 - len(ciphertext)%16)%16)
        S = self.ghash(H, auth_data + cipher_padded + len_block)
        tag = bytes(a ^ b for a, b in zip(self.encrypt_block(self.iv), S))
        return ciphertext, tag

    def gcm_decrypt(self, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> bytes:
        H = self.encrypt_block(b"\x00" * 16)
        plaintext = self.ctr_decrypt(ciphertext)
        len_block = (len(aad)*8).to_bytes(8, 'big') + (len(ciphertext)*8).to_bytes(8, 'big')
        auth_data = aad + b"\x00"*((16 - len(aad)%16)%16)
        cipher_padded = ciphertext + b"\x00"*((16 - len(ciphertext)%16)%16)
        S = self.ghash(H, auth_data + cipher_padded + len_block)
        calc_tag = bytes(a ^ b for a, b in zip(self.encrypt_block(self.iv), S))
        if calc_tag != tag:
            raise ValueError("Authentication failed: invalid tag.")
        return plaintext

    # === AES-XTS ===
    @staticmethod
    def gf128mulx(tweak: bytes) -> bytes:
        t = int.from_bytes(tweak, 'little')
        carry = (t >> 127) & 1
        t = ((t << 1) & ((1 << 128) - 1))
        if carry:
            t ^= 0x87
        return t.to_bytes(16, 'little')

    def xts_encrypt(self, data: bytes, sector_number: int = 0) -> bytes:
        if self.mode != AESMode.XTS:
            raise ValueError("This method only works in XTS mode.")
        out = b""
        tweak = self.aes2.encrypt_block(sector_number.to_bytes(16, 'little'))
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            if len(block) < 16:
                # ciphertext stealing
                last_full = out[-16:]
                new_last = bytes(a ^ b for a,b in zip(last_full[:len(block)], block))
                out = out[:-16] + new_last
                block = block + b"\x00"*(16 - len(block))
            t_enc = bytes(a ^ b for a,b in zip(block, tweak))
            c = self.aes1.encrypt_block(t_enc)
            c = bytes(a ^ b for a,b in zip(c, tweak))
            out += c[:len(block)]
            tweak = self.gf128mulx(tweak)
        return out

    def xts_decrypt(self, data: bytes, sector_number: int = 0) -> bytes:
        if self.mode != AESMode.XTS:
            raise ValueError("This method only works in XTS mode.")
        out = b""
        tweak = self.aes2.encrypt_block(sector_number.to_bytes(16, 'little'))
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            if len(block) < 16:
                last_full = out[-16:]
                new_last = bytes(a ^ b for a,b in zip(last_full[:len(block)], block))
                out = out[:-16] + new_last
                block = block + b"\x00"*(16 - len(block))
            t_dec = bytes(a ^ b for a,b in zip(block, tweak))
            p = self.aes1.decrypt_block(t_dec)
            p = bytes(a ^ b for a,b in zip(p, tweak))
            out += p[:len(block)]
            tweak = self.gf128mulx(tweak)
        return out
    
    def ofb_encrypt(self, data: bytes) -> bytes:
        out = b""
        feedback = self.iv
        for i in range(0, len(data), 16):
            feedback = self.encrypt_block(feedback)
            block = data[i:i+16]
            enc = bytes(a ^ b for a, b in zip(block, feedback))
            out += enc
        return out
    
    def ofb_decrypt(self, data: bytes) -> bytes:
        return self.ofb_encrypt(data)
    
    def cfb_encrypt(self, data: bytes) -> bytes:
        out = b""
        feedback = self.iv
        for i in range(0, len(data), 16):
            feedback = self.encrypt_block(feedback)
            block = data[i:i+16]
            enc = bytes(a ^ b for a, b in zip(block, feedback))
            out += enc
            feedback = enc
        return out
    
    def cfb_decrypt(self, data: bytes) -> bytes:
        out = b""
        feedback = self.iv
        for i in range(0, len(data), 16):
            feedback_enc = self.encrypt_block(feedback)
            block = data[i:i+16]
            dec = bytes(a ^ b for a, b in zip(block, feedback_enc))
            out += dec
            feedback = block
        return out
    
    # === AES-CCM MODE ===
    def ccm_encrypt(self, data: bytes, aad: bytes = b"", tag_length: int = 16, nonce: bytes = None) -> tuple:
        """
        AES-CCM encryption (Counter with CBC-MAC)
        Returns (ciphertext, tag)
        """
        if nonce is None:
            nonce = self.iv
        if not (7 <= len(nonce) <= 13):
            raise ValueError("Nonce must be 7–13 bytes for CCM mode.")
        L = 15 - len(nonce)
        flags = ((aad and 1) << 6) | (((tag_length - 2)//2) << 3) | (L - 1)
        b0 = bytes([flags]) + nonce + len(data).to_bytes(L, 'big')

        mac = self.encrypt_block(b0)
        if aad:
            aad_len = len(aad).to_bytes(2, 'big')
            padded_aad = aad_len + aad
            padded_aad += b'\x00' * ((16 - len(padded_aad) % 16) % 16)
            for i in range(0, len(padded_aad), 16):
                block = padded_aad[i:i+16]
                mac = self.encrypt_block(bytes(a ^ b for a, b in zip(mac, block)))

        for i in range(0, len(data), 16):
            block = data[i:i+16].ljust(16, b'\x00')
            mac = self.encrypt_block(bytes(a ^ b for a, b in zip(mac, block)))

        # CTR encryption
        ctr_prefix = bytes([(L - 1)]) + nonce
        ciphertext = b""
        counter = 1
        for i in range(0, len(data), 16):
            counter_block = ctr_prefix + counter.to_bytes(L, 'big')
            s = self.encrypt_block(counter_block)
            block = data[i:i+16]
            enc = bytes(a ^ b for a, b in zip(block, s))
            ciphertext += enc[:len(block)]
            counter += 1

        # Tag
        counter0 = ctr_prefix + (0).to_bytes(L, 'big')
        s0 = self.encrypt_block(counter0)
        tag = bytes(a ^ b for a, b in zip(mac, s0))[:tag_length]
        return ciphertext, tag

    def ccm_decrypt(self, ciphertext: bytes, tag: bytes, aad: bytes = b"", nonce: bytes = None) -> bytes:
        """
        AES-CCM decryption (with tag verification)
        """
        if nonce is None:
            nonce = self.iv
        if not (7 <= len(nonce) <= 13):
            raise ValueError("Nonce must be 7–13 bytes for CCM mode.")
        L = 15 - len(nonce)

        # CTR decryption
        ctr_prefix = bytes([(L - 1)]) + nonce
        plaintext = b""
        counter = 1
        for i in range(0, len(ciphertext), 16):
            counter_block = ctr_prefix + counter.to_bytes(L, 'big')
            s = self.encrypt_block(counter_block)
            block = ciphertext[i:i+16]
            dec = bytes(a ^ b for a, b in zip(block, s))
            plaintext += dec[:len(block)]
            counter += 1

        # Recompute tag for verification
        flags = ((aad and 1) << 6) | (((len(tag) - 2)//2) << 3) | (L - 1)
        b0 = bytes([flags]) + nonce + len(plaintext).to_bytes(L, 'big')

        mac = self.encrypt_block(b0)
        if aad:
            aad_len = len(aad).to_bytes(2, 'big')
            padded_aad = aad_len + aad
            padded_aad += b'\x00' * ((16 - len(padded_aad) % 16) % 16)
            for i in range(0, len(padded_aad), 16):
                block = padded_aad[i:i+16]
                mac = self.encrypt_block(bytes(a ^ b for a, b in zip(mac, block)))

        for i in range(0, len(plaintext), 16):
            block = plaintext[i:i+16].ljust(16, b'\x00')
            mac = self.encrypt_block(bytes(a ^ b for a, b in zip(mac, block)))

        counter0 = ctr_prefix + (0).to_bytes(L, 'big')
        s0 = self.encrypt_block(counter0)
        calc_tag = bytes(a ^ b for a, b in zip(mac, s0))[:len(tag)]

        if calc_tag != tag:
            raise ValueError("Authentication failed: CCM tag mismatch.")
        return plaintext
    
    def pcbc_encrypt(self, data: bytes) -> bytes:
        if self.mode in (AESMode.GCM, AESMode.XTS, AESMode.CCM):
            raise ValueError("Use dedicated encryptor for this mode.")
        data = pad(data)
        out = b""
        prev = self.iv
        prev_plain = bytes(16)
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            if self.mode == AESMode.CBC:
                block = bytes(a ^ b for a, b in zip(block, prev))
            elif self.mode == AESMode.PCBC:
                block = bytes(a ^ b ^ c for a, b, c in zip(block, prev, prev_plain))
            enc = self.encrypt_block(block)
            out += enc
            if self.mode == AESMode.CBC:
                prev = enc
            elif self.mode == AESMode.PCBC:
                prev_plain = block
                prev = enc
        return out

    def pcbc_decrypt(self, data: bytes) -> bytes:
        if self.mode in (AESMode.GCM, AESMode.XTS, AESMode.CCM):
            raise ValueError("Use dedicated decryptor for this mode.")
        out = b""
        prev = self.iv
        prev_plain = bytes(16)
        for i in range(0, len(data), 16):
            block = data[i:i+16]
            dec = self.decrypt_block(block)
            if self.mode == AESMode.CBC:
                dec = bytes(a ^ b for a, b in zip(dec, prev))
                prev = block
            elif self.mode == AESMode.PCBC:
                dec_plain = bytes(a ^ b ^ c for a, b, c in zip(dec, prev, prev_plain))
                prev_plain = dec_plain
                prev = block
                dec = dec_plain
            out += dec
        return unpad(out)
    
    # === AES-CMAC helper for SIV ===
    @staticmethod
    def cmac_subkey(aes):
        """Generate AES-CMAC subkeys (K1, K2)."""
        const_Rb = 0x87
        zero_block = b"\x00" * 16
        L = aes.encrypt_block(zero_block)
        def dbl(block):
            val = int.from_bytes(block, "big")
            val <<= 1
            if block[0] & 0x80:
                val ^= const_Rb
            return (val & ((1 << 128) - 1)).to_bytes(16, "big")
        K1 = dbl(L)
        K2 = dbl(K1)
        return K1, K2

    @staticmethod
    def aes_cmac(aes, msg: bytes) -> bytes:
        """AES-CMAC using the same AES instance."""
        K1, K2 = AES.cmac_subkey(aes)
        n = (len(msg) + 15) // 16
        if n == 0:
            n = 1
        last_block_complete = len(msg) % 16 == 0 and len(msg) != 0
        if last_block_complete:
            last_block = bytes(a ^ b for a, b in zip(msg[-16:], K1))
        else:
            pad_len = 16 - (len(msg) % 16)
            padded = msg + b"\x80" + b"\x00" * (pad_len - 1)
            last_block = bytes(a ^ b for a, b in zip(padded[-16:], K2))

        mac = b"\x00" * 16
        for i in range(0, len(msg) - 16, 16):
            block = msg[i:i+16]
            mac = aes.encrypt_block(bytes(a ^ b for a, b in zip(mac, block)))
        mac = aes.encrypt_block(bytes(a ^ b for a, b in zip(mac, last_block)))
        return mac

    # === AES-SIV (RFC 5297) ===
    def siv_encrypt(self, data: bytes, aad: bytes = b"") -> tuple:
        """
        AES-SIV encryption.
        Returns (ciphertext, tag)
        """
        if len(self.key) not in (32, 64):
            raise ValueError("AES-SIV requires 32 bytes (AES-128-SIV) or 64 bytes (AES-256-SIV) key.")
        half = len(self.key) // 2
        key_mac = self.key[:half]
        key_enc = self.key[half:]

        # Compute Synthetic IV using AES-CMAC
        aes_mac = AES(key_mac, AESMode.ECB)
        mac_input = aad + b"\x00" + data
        siv = AES.aes_cmac(aes_mac, mac_input)

        # Encrypt using AES-CTR with IV = SIV
        aes_ctr = AES(key_enc, AESMode.CTR, siv)
        ciphertext = aes_ctr.ctr_encrypt(data)
        return ciphertext, siv

    def siv_decrypt(self, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> bytes:
        """
        AES-SIV decryption with authentication.
        """
        if len(self.key) not in (32, 64):
            raise ValueError("AES-SIV requires 32 or 64 bytes key.")
        half = len(self.key) // 2
        key_mac = self.key[:half]
        key_enc = self.key[half:]

        # Decrypt first
        aes_ctr = AES(key_enc, AESMode.CTR, tag)
        plaintext = aes_ctr.ctr_decrypt(ciphertext)

        # Verify tag by recomputing SIV
        aes_mac = AES(key_mac, AESMode.ECB)
        mac_input = aad + b"\x00" + plaintext
        computed_tag = AES.aes_cmac(aes_mac, mac_input)
        if computed_tag != tag:
            raise ValueError("Authentication failed: SIV tag mismatch.")
        return plaintext
    
    # === AES-EAX (Authenticated Encryption) ===
    def eax_encrypt(self, data: bytes, nonce: bytes, aad: bytes = b"") -> tuple:
        """
        AES-EAX encryption (RFC 5116)
        Returns (ciphertext, tag)
        """
        if len(nonce) == 0:
            raise ValueError("Nonce must not be empty.")
        aes_mac = AES(self.key, AESMode.ECB)

        def omac(header: int, msg: bytes) -> bytes:
            """Compute CMAC with header domain separation."""
            return AES.aes_cmac(aes_mac, bytes([header]) + msg)

        # Domain-separated CMACs
        nonce_mac = omac(0, nonce)
        aad_mac   = omac(1, aad)

        # Encrypt with AES-CTR using IV = nonce_mac
        aes_ctr = AES(self.key, AESMode.CTR, nonce_mac)
        ciphertext = aes_ctr.ctr_encrypt(data)

        cipher_mac = omac(2, ciphertext)

        # Final tag
        tag = bytes(a ^ b ^ c for a, b, c in zip(nonce_mac, aad_mac, cipher_mac))
        return ciphertext, tag

    def eax_decrypt(self, ciphertext: bytes, nonce: bytes, tag: bytes, aad: bytes = b"") -> bytes:
        """
        AES-EAX decryption and tag verification.
        """
        if len(nonce) == 0:
            raise ValueError("Nonce must not be empty.")
        aes_mac = AES(self.key, AESMode.ECB)

        def omac(header: int, msg: bytes) -> bytes:
            return AES.aes_cmac(aes_mac, bytes([header]) + msg)

        nonce_mac = omac(0, nonce)
        aad_mac   = omac(1, aad)
        aes_ctr = AES(self.key, AESMode.CTR, nonce_mac)
        plaintext = aes_ctr.ctr_decrypt(ciphertext)
        cipher_mac = omac(2, ciphertext)

        calc_tag = bytes(a ^ b ^ c for a, b, c in zip(nonce_mac, aad_mac, cipher_mac))
        if calc_tag != tag:
            raise ValueError("Authentication failed: invalid EAX tag.")
        return plaintext
    
    # === AES-OCB3 (Offset Codebook Mode v3) ===
    def ocb3_encrypt(self, data: bytes, nonce: bytes, aad: bytes = b"", tag_length: int = 16) -> tuple:
        """
        AES-OCB3 encryption with authentication.
        Returns (ciphertext, tag)
        """
        if len(nonce) not in range(1, 16):
            raise ValueError("Nonce must be 1–15 bytes for OCB3.")
        block_size = 16

        def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))
        def ntz(x): return (x & -x).bit_length() - 1

        # === Generate masks ===
        L_star = self.encrypt_block(b"\x00" * block_size)
        def dbl(block):
            val = int.from_bytes(block, "big")
            val <<= 1
            if block[0] & 0x80:
                val ^= 0x87
            return (val & ((1 << 128) - 1)).to_bytes(16, "big")

        L_dollar = dbl(L_star)
        L = [dbl(L_dollar)]
        for _ in range(1, 64):
            L.append(dbl(L[-1]))

        # === Nonce processing ===
        nonce_pad = (b"\x00" * (block_size - len(nonce) - 1)) + bytes([len(nonce) * 8]) + nonce
        nonce_block = bytearray(nonce_pad)
        nonce_block[0] = nonce_block[0] & 0x7F
        nonce_tag = self.encrypt_block(bytes(nonce_block))
        Offset_0 = nonce_tag
        Checksum = b"\x00" * block_size
        Offset_i = Offset_0
        ciphertext = b""

        # === Encrypt full blocks ===
        i = 1
        for j in range(0, len(data) - len(data) % block_size, block_size):
            block = data[j:j+block_size]
            Offset_i = xor(Offset_i, L[ntz(i)])
            P_i = xor(block, Offset_i)
            C_i = xor(self.encrypt_block(P_i), Offset_i)
            ciphertext += C_i
            Checksum = xor(Checksum, block)
            i += 1

        # === Last partial block ===
        last = data[len(data) - len(data) % block_size:]
        if last:
            Offset_star = xor(Offset_i, L_star)
            Pad = self.encrypt_block(Offset_star)
            C_last = bytes(a ^ b for a, b in zip(last, Pad[:len(last)]))
            ciphertext += C_last
            Checksum = xor(Checksum, last + b"\x80" + b"\x00"*(block_size - len(last) - 1))
        else:
            Offset_star = xor(Offset_i, L_dollar)

        # === Tag computation ===
        Offset_m = Offset_star if last else Offset_i
        Tag = xor(self.encrypt_block(xor(Checksum, Offset_m)), self.encrypt_block(xor(L_star, nonce_tag)))

        # === AAD processing ===
        if aad:
            aad_sum = b"\x00" * block_size
            a_i = 1
            for j in range(0, len(aad) - len(aad) % block_size, block_size):
                Offset_a = xor(L[ntz(a_i)], b"\x00" * block_size)
                aad_sum = xor(aad_sum, self.encrypt_block(xor(aad[j:j+block_size], Offset_a)))
                a_i += 1
            last_aad = aad[len(aad) - len(aad) % block_size:]
            if last_aad:
                Offset_a = xor(L_star, b"\x00" * block_size)
                pad_a = self.encrypt_block(Offset_a)
                padded = bytes(a ^ b for a, b in zip(last_aad, pad_a[:len(last_aad)]))
                aad_sum = xor(aad_sum, padded + b"\x80" + b"\x00"*(block_size - len(last_aad) - 1))
            Tag = xor(Tag, self.encrypt_block(xor(aad_sum, L_dollar)))

        return ciphertext, Tag[:tag_length]

    def ocb3_decrypt(self, ciphertext: bytes, nonce: bytes, tag: bytes, aad: bytes = b"") -> bytes:
        """
        AES-OCB3 decryption with tag verification.
        """
        block_size = 16
        def xor(a, b): return bytes(x ^ y for x, y in zip(a, b))
        def ntz(x): return (x & -x).bit_length() - 1

        L_star = self.encrypt_block(b"\x00" * block_size)
        def dbl(block):
            val = int.from_bytes(block, "big")
            val <<= 1
            if block[0] & 0x80:
                val ^= 0x87
            return (val & ((1 << 128) - 1)).to_bytes(16, "big")

        L_dollar = dbl(L_star)
        L = [dbl(L_dollar)]
        for _ in range(1, 64):
            L.append(dbl(L[-1]))

        nonce_pad = (b"\x00" * (block_size - len(nonce) - 1)) + bytes([len(nonce) * 8]) + nonce
        nonce_block = bytearray(nonce_pad)
        nonce_block[0] = nonce_block[0] & 0x7F
        nonce_tag = self.encrypt_block(bytes(nonce_block))
        Offset_0 = nonce_tag
        Checksum = b"\x00" * block_size
        Offset_i = Offset_0
        plaintext = b""

        i = 1
        for j in range(0, len(ciphertext) - len(ciphertext) % block_size, block_size):
            block = ciphertext[j:j+block_size]
            Offset_i = xor(Offset_i, L[ntz(i)])
            C_i = xor(block, Offset_i)
            P_i = xor(self.decrypt_block(C_i), Offset_i)
            plaintext += P_i
            Checksum = xor(Checksum, P_i)
            i += 1

        last = ciphertext[len(ciphertext) - len(ciphertext) % block_size:]
        if last:
            Offset_star = xor(Offset_i, L_star)
            Pad = self.encrypt_block(Offset_star)
            P_last = bytes(a ^ b for a, b in zip(last, Pad[:len(last)]))
            plaintext += P_last
            Checksum = xor(Checksum, P_last + b"\x80" + b"\x00"*(block_size - len(P_last) - 1))
        else:
            Offset_star = xor(Offset_i, L_dollar)

        Offset_m = Offset_star if last else Offset_i
        Tag_check = xor(self.encrypt_block(xor(Checksum, Offset_m)), self.encrypt_block(xor(L_star, nonce_tag)))

        if aad:
            aad_sum = b"\x00" * block_size
            a_i = 1
            for j in range(0, len(aad) - len(aad) % block_size, block_size):
                Offset_a = xor(L[ntz(a_i)], b"\x00" * block_size)
                aad_sum = xor(aad_sum, self.encrypt_block(xor(aad[j:j+block_size], Offset_a)))
                a_i += 1
            last_aad = aad[len(aad) - len(aad) % block_size:]
            if last_aad:
                Offset_a = xor(L_star, b"\x00" * block_size)
                pad_a = self.encrypt_block(Offset_a)
                padded = bytes(a ^ b for a, b in zip(last_aad, pad_a[:len(last_aad)]))
                aad_sum = xor(aad_sum, padded + b"\x80" + b"\x00"*(block_size - len(last_aad) - 1))
            Tag_check = xor(Tag_check, self.encrypt_block(xor(aad_sum, L_dollar)))

        if Tag_check[:len(tag)] != tag:
            raise ValueError("Authentication failed: invalid OCB3 tag.")
        return plaintext