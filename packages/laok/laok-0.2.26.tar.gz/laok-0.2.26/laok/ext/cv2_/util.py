#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/11 22:42:30

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['keep_uint8', 'keep_int32', 'new_color', 'new_gray']

def keep_uint8(data):
    return np.array(data, dtype=np.uint8)

def keep_int32(data):
    return np.array(data, dtype=np.int32)

def new_color(width=512, height=512, color=(0,0,0), dtype=np.uint8):
    return np.full((height, width, 3), fill_value=color, dtype=dtype)

def new_gray(width=512, height=512, value=0, dtype=np.uint8):
    return np.full( (height, width), fill_value=value, dtype=dtype)

