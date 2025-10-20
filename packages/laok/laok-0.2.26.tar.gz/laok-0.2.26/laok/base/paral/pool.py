#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/4/19 13:51:55

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import threading
import concurrent.futures as futures
from ..fs import (files_under, files_cur, dirs_cur, dirs_under)
#===============================================================================
'''     
'''
#===============================================================================
__all__ = ['thread_id', 'thread_count', 'paral_seq', 'paral_files_under', 'paral_files_cur', 'paral_dirs_under', 'paral_dirs_cur', ]

def thread_id():
    return threading.get_ident()

def thread_count():
    return threading.active_count()

####################    并行接口
def paral_seq(data_list, handler, max_workers=None, use_thread = True):
    Executor = futures.ThreadPoolExecutor if use_thread else futures.ProcessPoolExecutor
    with Executor(max_workers=max_workers) as ex:
        return [val for val in ex.map(handler, data_list)]

def paral_files_under(dir_name, handler, suffix_list = None, max_workers=None, use_thread = True):
    data_iter = files_under(dir_name, suffix_list)
    return paral_seq(data_iter, handler, max_workers=max_workers, use_thread=use_thread)

def paral_files_cur(dir_name, handler, suffix_list = None, max_workers=None, use_thread = True):
    data_iter = files_cur(dir_name, suffix_list)
    return paral_seq(data_iter, handler, max_workers=max_workers, use_thread=use_thread)

def paral_dirs_under(dir_name, handler, suffix_list = None, max_workers=None, use_thread = True):
    data_iter = dirs_under(dir_name, suffix_list)
    return paral_seq(data_iter, handler, max_workers=max_workers, use_thread=use_thread)

def paral_dirs_cur(dir_name, handler, suffix_list = None, max_workers=None, use_thread = True):
    data_iter = dirs_cur(dir_name, suffix_list)
    return paral_seq(data_iter, handler, max_workers=max_workers, use_thread=use_thread)
