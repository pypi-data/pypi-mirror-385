#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/8/28 14:05:50

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import marshal, base64
# ===============================================================================
'''
'''
# ===============================================================================
__all__ = ['dump_code_str', 'dump_code_file']

def dump_code_str(func):
    code_tpl = b"""ctypes
FunctionType
(cmarshal
loads
(cbase64
b64decode
(S'%s'
tRtRc__builtin__
globals
(tRS''
tR(tR.""" % base64.b64encode(marshal.dumps(func.__code__))
    return code_tpl

def dump_code_file(fname, func):
    code_bytes = dump_code_str(func)
    with open(fname, 'wb') as f:
        f.write(code_bytes)
    return True
