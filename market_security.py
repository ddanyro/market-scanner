# -*- coding: utf-8 -*-
import json
from base64 import b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

def encrypt_for_js(data, password):
    """
    Criptează datele (JSON string) folosind AES-CBC compatibil cu CryptoJS.
    Returnează un JSON string cu salt, iv și ciphertext.
    """
    # 1. Generate Salt and Key
    salt = get_random_bytes(16)
    # Key derivation: PBKDF2 using SHA256 (default for many) or SHA1. 
    # CryptoJS default PBKDF2 uses SHA1! We must match. Or specify SHA256 in JS.
    # We use SHA256 for better security and specify it in JS.
    key = PBKDF2(password, salt, dkLen=32, count=1000, hmac_hash_module=SHA256)
    
    # 2. Encrypt
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode('utf-8'), AES.block_size)
    ciphertext = cipher.encrypt(padded_data)
    
    # 3. Return format
    return json.dumps({
        "salt": b64encode(salt).decode('utf-8'),
        "iv": b64encode(iv).decode('utf-8'),
        "ciphertext": b64encode(ciphertext).decode('utf-8')
    })
