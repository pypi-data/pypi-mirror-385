#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/12/23 08:12:33

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import shutil
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['path_copy' ]

def path_copy(src, dst, follow_symlinks=True):
    shutil.copy(src, dst, follow_symlinks=follow_symlinks)

