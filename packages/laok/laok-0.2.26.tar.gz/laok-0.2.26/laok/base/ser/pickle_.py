#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 19:59:14

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import pickle
# ===============================================================================
#
# ===============================================================================
__all__ = ['save_pickle_file', 'load_pickle_file']

def save_pickle_file(filename, obj, **kws):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f, **kws)
    return True

def load_pickle_file(filename, **kws):
    with open(filename, 'rb') as f:
        return pickle.load(f, **kws)

