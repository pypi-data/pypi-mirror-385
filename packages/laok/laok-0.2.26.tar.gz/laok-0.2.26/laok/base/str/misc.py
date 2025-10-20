#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/6/1 15:25:00

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from io import StringIO
from pprint import pprint
#===============================================================================
'''     
'''
#===============================================================================
__all__ = [ 'pprint_str', 'val_to_list',
            'dict_to_str', 'parse_index_list']

def pprint_str(obj, indent=4, width=80, depth=None, compact=False, sort_dicts=True):
    s = StringIO()
    pprint(obj, s, indent=indent, width=width, depth=depth, compact=compact, sort_dicts=sort_dicts)
    return s.getvalue()

def val_to_list(val, sep=';'):
    if val is None:
        return ()
    if isinstance(val, (list,tuple)):
        return val
    if isinstance(val, str):
        return val.split(sep)
    return val



def dict_to_str(obj, start=10, stop=10):
    sz = len(obj)
    _istart = start
    _iend = sz - stop
    _once = True

    ss = StringIO()
    for i, (k, v) in enumerate(obj.items()):
        if i < _istart or i >= _iend:
            ss.write(f'{k}={v}\n')
        else:
            if _once:
                ss.write('... ...\n')
                _once = False
    return ss.getvalue()

def parse_index_list(val_list):
    idx_list = []
    for v in val_list:
        if isinstance(v, int):
            idx_list.append(v)
        elif isinstance(v, str):
            segs = v.split('-')
            if len(segs) == 1:
                idx_list.append(int(v))
            elif len(segs) == 2:
                _v1, _v2 = int(segs[0]), int(segs[1])
                idx_list.extend(range(_v1, _v2+1))
    return idx_list

