#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 01:18:03

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['load_cld_xyz', 'load_cld_bin', 'save_cld_xyz']

def load_cld_xyz(filename, delimiter=',', **kws):
    return np.loadtxt(filename, delimiter=delimiter, **kws)

def save_cld_xyz(filename, points, delimiter=',', **kws):
    np.savetxt(filename, points, delimiter=delimiter, **kws)

def load_cld_bin(filename, feature=4):
    return np.fromfile(filename, dtype=np.float32).reshape((-1, feature))

