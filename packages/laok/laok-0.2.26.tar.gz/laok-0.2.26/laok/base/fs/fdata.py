#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 10:05:28

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from .fpath import path_exist
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['file_read_text', 'file_write_text', 'file_read_lines', 'file_write_lines',
           'file_read_bin', 'file_read_chunk', 'file_write_bin',
           'file_text_reader', 'file_bin_reader',
           'file_bin_writer', 'file_text_writer',
           'file_list_merge'
           ]

def file_text_reader(fname, encoding='utf8'):
    return open(fname, mode='r', encoding=encoding)

def file_bin_reader(fname):
    return open(fname, mode='rb')

def file_text_writer(fname, encoding='utf8'):
    return open(fname, mode='w', encoding=encoding)

def file_bin_writer(fname):
    return open(fname, mode='wb')

def file_read_text(fname, encoding='utf8'):
    with open(fname, mode='r', encoding=encoding) as f:
        return f.read()
    return fname

def file_write_text(fname, text, encoding='utf8', skip_exist=False):
    if skip_exist and path_exist(fname):
        return fname
    with open(fname, mode='w', encoding=encoding) as f:
        f.write(text)
    return fname

def file_read_lines(fname, encoding='utf8', strip = True, skip_empty=False):
    with open(fname, mode='r', encoding=encoding) as f:
        for line in f:
            if strip:
                line = line.strip()
            if skip_empty:
                if not line :
                    continue
            yield line

def file_write_lines(fname, lines, encoding='utf8', line_append='\n', skip_exist=False):
    if skip_exist and path_exist(fname):
        return fname

    with open(fname, mode='w', encoding=encoding) as f:
        for line in lines:
            f.write(line + line_append)
    return fname

def file_read_bin(fname):
    with open(fname, mode='rb') as f:
        return f.read()
    return fname

def file_read_chunk(fname, buf_size=1e6):
    buf_size = int(buf_size)
    with open(fname, mode='rb') as f:
        while True:
            data = f.read(buf_size)
            if not data:
                break
            yield data

def file_write_bin(fname, data, skip_exist=False):
    if skip_exist and path_exist(fname):
        return fname
    with open(fname, mode='wb') as f:
        f.write(data)
    return fname

def file_list_merge(file_list, dst_file, buf_size=1e6):
    with file_bin_writer(dst_file) as df:
        for fname in file_list:
            for data in file_read_chunk(fname, buf_size=buf_size):
                df.write(data)
    return dst_file