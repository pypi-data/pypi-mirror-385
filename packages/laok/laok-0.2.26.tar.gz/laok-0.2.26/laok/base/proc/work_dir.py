#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 14:13:38

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
from contextlib import contextmanager
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['workdir_get', 'workdir_set', 'workdir_scope']
def workdir_get():
    return os.getcwd()

def workdir_set(fpath):
    os.chdir(fpath)

@contextmanager
def workdir_scope(dir):
    try:
        old_dir = workdir_get()
        yield os.chdir(dir)
    finally:
        workdir_set(old_dir)