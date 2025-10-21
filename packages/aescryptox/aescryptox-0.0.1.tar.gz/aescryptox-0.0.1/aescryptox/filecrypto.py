import os
from .aes import AES
from .modes import AESMode
from .utils import random_bytes
from .hmac_sha256 import HMAC_SHA256

class AESFile:
    """Encrypt and decrypt files with AES (ECB, CBC, PCBC, CTR, GCM, CCM, XTS, SIV, EAX, OFB, CFB)."""

    @staticmethod
    def encrypt_file(input_path, output_path, key, mode=AESMode.CBC, use_hmac=True, sector_number: int = 0):
        iv = random_bytes(16)
        aes = AES(key, mode, iv)
        hmac_obj = HMAC_SHA256(key) if use_hmac else None

        with open(input_path, "rb") as fin, open(output_path, "wb") as fout:
            fout.write(mode.encode("utf-8").ljust(8, b" "))
            fout.write(iv)

            if mode == AESMode.EAX:
                data = fin.read()
                ciphertext, tag = aes.eax_encrypt(data, nonce=iv)
                fout.write(ciphertext)
                fout.write(tag)
                return

            if mode == AESMode.SIV:
                data = fin.read()
                ciphertext, tag = aes.siv_encrypt(data)
                fout.write(ciphertext)
                fout.write(tag)
                return

            if mode == AESMode.GCM:
                data = fin.read()
                ciphertext, tag = aes.gcm_encrypt(data)
                fout.write(ciphertext)
                fout.write(tag)
                return

            if mode == AESMode.CCM:
                data = fin.read()
                ciphertext, tag = aes.ccm_encrypt(data)
                fout.write(ciphertext)
                fout.write(tag)
                return
            
            if mode == AESMode.OCB3:
                data = fin.read()
                ciphertext, tag = aes.ocb3_encrypt(data, nonce=iv)
                fout.write(ciphertext)
                fout.write(tag)
                return

            while chunk := fin.read(1024):
                enc = aes.encrypt(chunk)
                fout.write(enc)
                if use_hmac and mode not in (AESMode.GCM, AESMode.CCM, AESMode.SIV, AESMode.EAX):
                    hmac_obj.digest(enc)

            if use_hmac and mode not in (AESMode.GCM, AESMode.CCM, AESMode.XTS, AESMode.SIV, AESMode.EAX):
                fout.write(hmac_obj.digest(iv))

    @staticmethod
    def decrypt_file(input_path, output_path, key, mode: str = None, use_hmac=True, sector_number: int = 0):
        with open(input_path, "rb") as fin:
            header_mode = fin.read(8).strip().decode("utf-8")
            mode = mode or header_mode
            iv = fin.read(16)
            data = fin.read()
            if not data:
                raise ValueError("Ciphertext is empty or corrupted.")
            aes = AES(key, mode, iv)

            if mode == AESMode.EAX:
                ciphertext, tag = data[:-16], data[-16:]
                dec = aes.eax_decrypt(ciphertext, nonce=iv, tag=tag)
                with open(output_path, "wb") as fout:
                    fout.write(dec)
                return

            if mode == AESMode.SIV:
                ciphertext, tag = data[:-16], data[-16:]
                dec = aes.siv_decrypt(ciphertext, tag)
                with open(output_path, "wb") as fout:
                    fout.write(dec)
                return

            if mode == AESMode.GCM:
                ciphertext, tag = data[:-16], data[-16:]
                dec = aes.gcm_decrypt(ciphertext, tag)
                with open(output_path, "wb") as fout:
                    fout.write(dec)
                return

            if mode == AESMode.CCM:
                ciphertext, tag = data[:-16], data[-16:]
                dec = aes.ccm_decrypt(ciphertext, tag)
                with open(output_path, "wb") as fout:
                    fout.write(dec)
                return
            
            if mode == AESMode.OCB3:
                ciphertext, tag = data[:-16], data[-16:]
                dec = aes.ocb3_decrypt(ciphertext, nonce=iv, tag=tag)
                with open(output_path, "wb") as fout:
                    fout.write(dec)
                return

            if use_hmac:
                data = data[:-32]

            dec = aes.decrypt(data)
            with open(output_path, "wb") as fout:
                fout.write(dec)
