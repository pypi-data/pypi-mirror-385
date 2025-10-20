#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/8/13 10:14:58

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from collections import OrderedDict
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['load_csv', 'save_csv']

def load_csv(fname):
    ret = OrderedDict()
    with open(fname, mode='r', encoding='utf8') as f:
        fields = f.readline().strip().split(',')
        for field in fields:
            ret[field] = []

        for line in f:
            for i,seg in enumerate(line.strip().split(',')):
                ret[fields[i]].append(seg)
    return ret

def save_csv(fname):
    pass