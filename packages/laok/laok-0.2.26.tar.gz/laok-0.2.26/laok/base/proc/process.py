#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/30 10:49:47

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
from ..log import log_debug
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['system']


def system(cmd):
    log_debug(cmd)
    return os.system(cmd)

