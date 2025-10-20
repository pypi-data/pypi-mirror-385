#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/6/10 09:07:13

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''

# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['s2bool', 's2float']

def s2bool(v, default=None):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    return default

def s2float(val, default=None):
    try:
        return float(val)
    except:
        return default