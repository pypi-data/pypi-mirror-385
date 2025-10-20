#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/30 10:55:47

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
#===============================================================================
r'''
'''
#===============================================================================
__all__ = [
           'cur_line_num', 'cur_func_name', 'cur_func_kws',
           ]

def cur_line_num(depth = 1):
    '''获取当前行号'''
    return sys._getframe(depth).f_lineno

def cur_func_name(depth = 1):
    '''获取当前函数名字 '''
    return sys._getframe(depth).f_code.co_name

def cur_func_kws(depth = 1, skip_names = ("self", "cls")):
    ''' 获取函数的参数 '''
    _locals = sys._getframe(depth).f_locals.copy()
    if skip_names:
        if isinstance(skip_names, str):
            _locals.pop(skip_names, None)
        else:
            for name in skip_names:
                _locals.pop(name, None)
    return _locals
