#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 23:13:49

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['print_data']

def print_data(data, **kws):
    '''print detail data information
    '''
    if isinstance(data, np.ndarray):
        _print_arrary(data, **kws)
    else:
        msg = f'type[{type(data)}] id[{id(data)}]\n ' \
              f'{data}'
        print(msg)

def _print_arrary(data, show_content=True):
    msg = f'type[{type(data)}] ' \
          f'shape[{data.shape}]  ' \
          f'dtype[{data.dtype}]  ' \
          f'id[{id(data)}]\n'
    if show_content:
        msg += f'{data}'
    print(msg)
