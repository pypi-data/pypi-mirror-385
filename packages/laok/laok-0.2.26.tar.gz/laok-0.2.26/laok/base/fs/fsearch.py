#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/5/4 18:45:40
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from .fwalk import files_cur, files_under, path_sep
from .fpath import path_stem, path_basename
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['path_search_cur_file', 'path_search_under_file',
           'path_search_cur_stem', 'path_search_under_stem',
           'path_search_cur_ext', 'path_search_under_ext',
           ]

def path_search_cur_file(dir_names, filename, suffixes = None):
    _val_list = path_sep(filename)
    for fname in files_cur(dir_names, suffixes):
        if path_basename(fname) in _val_list:
            return fname

def path_search_under_file(dir_names, filename, suffixes = None):
    _val_list = path_sep(filename)
    for fname in files_under(dir_names, suffixes):
        if path_basename(fname) in _val_list:
            return fname


def path_search_cur_stem(dir_names, stem, suffixes = None):
    _val_list = path_sep(stem)
    for fname in files_cur(dir_names, suffixes):
        if path_stem(fname) in _val_list:
            return fname


def path_search_under_stem(dir_names, stem, suffixes = None):
    _val_list = path_sep(stem)
    for fname in files_under(dir_names, suffixes):
        if path_stem(fname) in _val_list:
            return fname

def path_search_cur_ext(dir_names,  suffixes):
    for fname in files_cur(dir_names, suffixes):
        return fname


def path_search_under_ext(dir_names, suffixes):
    for fname in files_under(dir_names, suffixes):
        return fname
