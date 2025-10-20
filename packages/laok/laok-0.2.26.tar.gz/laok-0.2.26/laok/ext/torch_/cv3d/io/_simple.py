#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/9/16 16:17:55

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['load_cld_xyz', 'load_cld_bin', 'save_cld_xyz', 'save_cld_bin']

def load_cld_xyz(filename, delimiter=','):
    return np.loadtxt(filename, delimiter=delimiter)

def load_cld_bin(filename, feature=4):
    return np.fromfile(filename, dtype=np.float32).reshape((-1, feature))

def save_cld_xyz(filename, obj, delimiter=','):
    return np.savetxt(filename, obj, fmt='%.6f', delimiter=delimiter)

def save_cld_bin(filename, obj):
    return obj.tofile(filename)
