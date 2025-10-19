#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Last modified: 2020-06-14 19:33:33
'''

import base64
import binascii

import base62
import rsa
from Crypto.Cipher import AES, DES

from .base_utils import to_bytes, to_str


def _unpad(s):
    ''' 删除 PKCS#7 方式填充的字符串
    '''
    return s[:-ord(s[len(s) - 1:])]


def _pad(text, size=8):
    length = len(text)
    val = size - (length % size)
    pad = f'{val:02x}' * val
    return text + binascii.unhexlify(pad)


def encode(text, lib='base62'):
    """ Return: str
    """
    if lib == 'base62':
        return base62.encodebytes(to_bytes(text))
    elif lib == 'base64':
        return to_str(base64.b64encode(to_bytes(text)))
    else:
        return to_str(binascii.b2a_hex(to_bytes(text)))


def decode(text, lib='base62'):
    """ Return: bytes
    """
    if lib == 'base62':
        return base62.decodebytes(to_str(text))
    elif lib == 'base64':
        return base64.b64decode(text)
    else:
        return binascii.a2b_hex(text)


def xor_encrypt(text: str, key: int, lib='base64'):
    encrypted = ''.join([chr(ord(x) ^ ord(chr(key))) for x in to_str(text)])
    return encode(encrypted, lib)


def xor_decrypt(ciphertext: str, key: int, lib='base64'):
    data = decode(ciphertext, lib)
    decrypted = ''.join([chr(ord(x) ^ ord(chr(key))) for x in to_str(data)])
    return to_str(decrypted)


def des_encrypt(text, key, iv=None, mode=DES.MODE_CBC, lib='base64'):
    ''' key: 8位 '''
    data = _pad(to_bytes(text), DES.block_size)
    key = to_bytes(key)
    iv = iv or key[:8]
    cipher = DES.new(key, mode, iv)
    encrypted = cipher.encrypt(data)
    return encode(encrypted, lib)


def des_decrypt(ciphertext, key, iv=None, mode=DES.MODE_CBC, lib='base64'):
    data = decode(ciphertext, lib)
    key = to_bytes(key)
    iv = iv or key[:8]
    cipher = DES.new(key, mode, iv)
    return to_str(_unpad(cipher.decrypt(data)))


def aes_encrypt(text, key, iv=None, mode=AES.MODE_CBC, lib='base64'):
    ''' key: 32位, iv: 16位 '''
    data = _pad(to_bytes(text), AES.block_size)
    key = to_bytes(key)
    iv = iv or key[:16]
    cipher = AES.new(key, mode, iv)
    encrypted = cipher.encrypt(data)
    return encode(encrypted, lib)


def aes_decrypt(ciphertext, key, iv=None, mode=AES.MODE_CBC, lib='base64'):
    data = decode(ciphertext, lib)
    key = to_bytes(key)
    iv = iv or key[:16]
    cipher = AES.new(key, mode, iv)
    return to_str(_unpad(cipher.decrypt(data)))


def gen_rsa_key(length=1024):
    pubkey, privkey = rsa.newkeys(length)
    return pubkey.save_pkcs1(), privkey.save_pkcs1()


def rsa_encrypt(data, pubkey):
    if not isinstance(pubkey, rsa.PublicKey):
        pubkey = rsa.PublicKey.load_pkcs1(to_bytes(pubkey))
    encrypted = rsa.encrypt(to_bytes(data), pubkey)
    return to_str(binascii.b2a_hex(encrypted))


def rsa_decrypt(ciphertext, privkey):
    if not isinstance(privkey, rsa.PrivateKey):
        privkey = rsa.PrivateKey.load_pkcs1(to_bytes(privkey))
    data = binascii.a2b_hex(ciphertext)
    return to_str(rsa.decrypt(data, privkey))
