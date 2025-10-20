#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 14:32:07
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['load_np_file', 'save_np_file', 'save_npz_file']
def load_np_file(filename, encoding='ASCII'):
    return np.load(filename, encoding=encoding)

def save_np_file(filename, arr):
    return np.save(filename, arr)

def save_npz_file(filename, *args, **kwds):
    return np.savez(filename, *args, **kwds)
