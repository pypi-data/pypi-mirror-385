#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/8/31 20:14:34

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import sys, types
import inspect as inspect
from pprint import pprint
# ===============================================================================
r'''提供一些调试方便的函数
'''
# ===============================================================================
__all__ = ['pprint',
           'print_args','print_eval',
           'print_type', 'print_repr', 'print_signature',
           ]

def print_args(*args, **kws):
    print('args:', args)
    print('kws:', kws)

def print_eval(st):
    '''字符串打印并执行'''
    _frm = sys._getframe(1)
    val = eval(st, _frm.f_globals, _frm.f_locals)
    print( f"{st} = {val}")

def print_type(t):
    '''打印类别'''
    _type_name = None
    for tname in dir(types):
        if tname[0].isupper() and isinstance(t, getattr(types, tname)):
            _type_name = tname
            break
    if _type_name is None:
        _type_name = f"{type(t)}"
    print(_type_name)

def print_repr(v):
    '''打印 repr '''
    print(repr(v))

def print_signature(func):
    sig = inspect.signature(func)
    print(f'{func.__name__}{str(sig)}')

