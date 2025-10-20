#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/23 21:15:54

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['env_value', 'env_values', 'env_files', 'env_file', 'env_exe_file']

def env_value(key, default=None):
    return os.getenv(key, default=default)

def env_values(key):
    return env_value(key, '').split(';')

def env_files(fname, key='PATH'):
    for pth in env_values(key):
        full_path = os.path.join(pth, fname)
        if os.path.exists(full_path):
            yield full_path

def env_file(fname, key='PATH'):
    for f in env_files(fname, key):
        return f

def env_exe_file(fname):
    exe_file = os.path.splitext(fname)[0] + ".exe"
    for pth in env_values('PATH'):
        full_path = os.path.join(pth, exe_file)
        if os.path.exists(full_path):
            return full_path