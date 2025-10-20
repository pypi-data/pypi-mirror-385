#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 19:56:18

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import json
# ===============================================================================
r'''json 读写
'''
# ===============================================================================
__all__ = ['save_json_file', 'load_json_file']

def save_json_file(filename, obj, *, skipkeys=False, ensure_ascii=False, check_circular=True,
                   allow_nan=True, cls=None, indent=2, separators=None,
                   default=None, sort_keys=False, **kw):
    with open(filename, mode='w', encoding='utf8') as f:
        json.dump(obj, f, skipkeys = skipkeys, ensure_ascii=ensure_ascii, check_circular=check_circular,
                allow_nan=allow_nan, cls=cls, indent=indent, separators=separators,
                default=default, sort_keys=sort_keys, **kw)
    return True

def load_json_file(filename, *, cls=None, object_hook=None, parse_float=None,
                    parse_int=None, parse_constant=None, object_pairs_hook=None, **kw):
    with open(filename, encoding='utf8') as f:
        return json.load(f, cls=cls, object_hook=object_hook, parse_float=parse_float,
                         parse_int=parse_int, parse_constant=parse_constant, object_pairs_hook=object_pairs_hook,
                         **kw)
