#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2021/3/27 14:18:09

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
import os.path as opath
from pathlib import Path
import shutil
#===============================================================================
#
#===============================================================================
__all__ = [ 'path_rename', 'path_native', 'path_unix', 'path_win', 'path_relative',
            'path_parent', 'path_make', 'path_make_parent',
            'path_join', 'path_abs', 'path_exist',
            'file_size', 'path_is_file', 'path_is_dir',
            'path_basename', 'path_stem', 'path_ext','path_add_ext', 'path_rm_ext',
            'path_replace_ext', 'path_replace_stem', 'path_replace_basename', 'path_replace_parent',
            'dirs_delete', 'file_delete', 'path_move',
            'path_deco_stem',
            ]

def path_rename(old_name, new_name):
    os.rename(old_name, new_name)

def path_native(fpath):
    return opath.normpath(fpath).replace('\\', '/').replace('/', os.sep)

def path_unix(fpath):
    return opath.normpath(fpath).replace('\\', '/')

def path_win(fpath):
    return opath.normpath(fpath).replace('/', '\\')

def path_relative(fpath, parent=None):
    return path_unix(os.path.relpath(fpath, parent))

def path_parent(fpath, level=1):
    '''fpath: 输入路径名字
       ret: 返回父路径
    '''
    p_path = fpath
    for i in range(0, level):
        p_path = path_unix(opath.split(p_path)[0])
    return p_path

def path_make(fpath):
    os.makedirs(fpath, exist_ok=True)
    return fpath

def path_make_parent(fpath):
    parent = path_parent(fpath)
    return path_make(parent)

def path_join(*args, make_parent=False):
    fpath = os.path.join(*args)
    if make_parent:
        path_make_parent(fpath)
    return path_unix(fpath)

def path_abs(fpath):
    return path_unix(os.path.abspath(fpath))

def path_exist(fpath):
    return fpath and os.path.exists(fpath)

def file_size(fpath):
    return os.path.getsize(fpath)

def path_is_file(fpath):
    return fpath and os.path.isfile(fpath)

def path_is_dir(fpath):
    return fpath and os.path.isdir(fpath)

def path_basename(fpath):
    return os.path.basename(fpath)

def path_stem(fpath):
    return Path(fpath).stem

def path_ext(fpath, need_dot = True):
    '''file_path: 输入路径名字
       ret: 返回后缀
    '''
    fname = opath.split(fpath)[1]
    ext = opath.splitext(fname)[1]
    if ext and not need_dot:
        return ext[1:]
    return ext

def path_add_ext(fpath, ext):
    if ext.startswith('.'):
        return fpath + ext
    else:
        return fpath + "." + ext

def path_rm_ext(fpath):
    return path_unix(opath.splitext(fpath)[0])

def path_replace_ext(file_path, ext):
    if isinstance(ext, str) and not ext.startswith('.'):
        ext = '.' + ext
    new_file = opath.splitext(file_path)[0] + ext
    return path_unix(new_file)

def path_replace_stem(file_path, basename):
    _dir, _fname = opath.split(file_path)
    _basename, _ext = opath.splitext(_fname)
    return path_join(_dir, basename + _ext)

def path_deco_stem(file_path, preffix='', suffix=''):
    _dir, _fname = opath.split(file_path)
    _basename, _ext = opath.splitext(_fname)
    return path_join(_dir, preffix + _basename + suffix + _ext)

def path_replace_basename(file_path, filename):
    _dir, _fname = opath.split(file_path)
    return path_join(_dir, filename)

def path_replace_parent(file_path, parent):
    _dir, _fname = opath.split(file_path)
    return path_join(parent, _fname)

def dirs_delete(dirpath):
    shutil.rmtree(dirpath)

def file_delete(fpath):
    os.remove(fpath)

def path_move(old, new):
    shutil.move(old, new)