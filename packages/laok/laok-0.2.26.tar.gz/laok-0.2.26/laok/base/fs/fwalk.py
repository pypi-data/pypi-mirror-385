#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 10:07:05

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os, pathlib
from .fpath import path_join
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['dirs_cur', 'dirs_under',
           'files_cur', 'files_under',
           'fname_endswith', 'path_sep'
           ]

def path_sep(val, sep=';'):
    if val is None:
        return ()
    if isinstance(val, (list,tuple)):
        return val
    if isinstance(val, pathlib.Path):
        return str(val)
    if isinstance(val, str):
        return val.split(sep)
    return val

def fname_endswith(fname, suffixes):
    if suffixes is None:
        return True
    _low_suffix_list = [s.lower() for s in path_sep(suffixes)]
    _low_fname = fname.lower()
    return any( (_low_fname.endswith(s) for s in _low_suffix_list) )

####################    通用遍历路径

def dirs_cur(dir_names, suffixes = None):
    '''
    dir_names: 路径,支持多个
    suffixes: 后缀列表,支持多个;用于筛选路径
    ret: 返回生成器
    '''
    for dir_name in path_sep(dir_names):
        for fname in os.listdir(dir_name):
            fpath = path_join(dir_name, fname)
            if os.path.isdir(fpath):
                if fname_endswith(fpath, suffixes):
                    yield fpath

def dirs_under(dir_names, suffixes = None):
    '''
    dir_names: 路径,支持多个
    suffixes: 后缀列表,支持多个;用于筛选路径
    ret: 返回生成器
    '''
    for dir_name in path_sep(dir_names):
        for fdir_name, sub_fdirs, files in os.walk(dir_name):
            for fname in sub_fdirs:
                if fname_endswith(fname, suffixes):
                    yield path_join(fdir_name, fname)

def files_under(dir_names, suffixes = None):
    '''
    dir_names: 路径,支持多个
    suffixes: 后缀列表,支持多个;用于筛选路径
    ret: 返回生成器
    '''
    for dir_name in path_sep(dir_names):
        for fdir_name, _sub_fdirs, files in os.walk(dir_name):
            for fname in files:
                if fname_endswith(fname, suffixes):
                    yield path_join(fdir_name, fname)

def files_cur(dir_names, suffixes = None):
    '''
    dir_names: 路径,支持多个
    suffixes: 后缀列表,支持多个;用于筛选路径
    ret: 返回生成器
    '''
    for dir_name in path_sep(dir_names):
        for fname in os.listdir(dir_name):
            fpath = path_join(dir_name, fname)
            if os.path.isfile(fpath):
                if fname_endswith(fname, suffixes):
                    yield fpath
