#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/5/4 23:20:49
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import platform
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['is_windows', 'is_linux']

def is_windows():
    return platform.system().lower() == 'windows'

def is_linux():
    return platform.system().lower() == 'linux'
