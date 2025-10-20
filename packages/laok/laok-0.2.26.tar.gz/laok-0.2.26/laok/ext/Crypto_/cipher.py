#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/3 12:54:29

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from laok.base.fs import file_read_chunk, file_bin_writer, file_read_bin, file_write_bin
from Crypto.Cipher import AES
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['aes_decrypt_cbc_data', 'aes_decrypt_cbc_file', 'aes_decrypt_cbc_file_']

def aes_decrypt_cbc_data(data, key, iv=b'0000000000000000', **kws):
    aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv, **kws)
    return aes.decrypt(data)

def aes_decrypt_cbc_file(infile, outfile, key, iv=b'0000000000000000', **kws):
    with file_bin_writer(outfile) as f:
        aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv, **kws)
        for data in file_read_chunk(infile):
            data = aes.decrypt(data)
            f.write(data)

def aes_decrypt_cbc_file_(fname, key, iv=b'0000000000000000', **kws):
    data = file_read_bin(fname)
    data = aes_decrypt_cbc_data(data, key, iv, **kws)
    file_write_bin(fname, data)
