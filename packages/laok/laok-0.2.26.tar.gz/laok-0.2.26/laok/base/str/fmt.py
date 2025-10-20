#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/21 17:31:13
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['fmt_size']

def fmt_size(sz):
    return '(' + ", ".join(str(i) for i in sz) + ')'
