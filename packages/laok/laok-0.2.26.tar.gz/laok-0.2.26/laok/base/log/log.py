#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/5/22 17:32:21

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import logging
import logging.handlers
import functools
#===============================================================================
'''     
'''
#===============================================================================
__all__ = [ 'get_logger',
            'log_set_format',
            'log_add_rotate_file',
            'log_add_file',
            'log_add_console',
]

_def_name = 'laok'
_def_fmt = '[%(asctime)s][%(levelname)s][%(name)s]%(message)s'
_def_fmt_func_line = '[%(asctime)s][%(levelname)s][%(name)s][%(filename)s][%(funcName)s][%(lineno)d] %(message)s'

_logger_cache = {}
logging.basicConfig(format=_def_fmt)

def log_set_format(fmt=None, logger=None):
    if not logger:
        logger = get_logger()
    for hdl in logger.handlers:
        hdl.setFormatter(logging.Formatter(fmt if fmt else _def_fmt))


def log_add_rotate_file(filename=None, fmt = None, logger=None):
    if not logger:
        logger = get_logger()
    handler = logging.handlers.RotatingFileHandler(
        filename if filename else logger.name + ".log",
        maxBytes=1024 * 1024 * 1024 * 1,
        backupCount=5,
    )
    handler.setFormatter(logging.Formatter(fmt if fmt else _def_fmt))
    logger.addHandler(handler)
    return handler

def log_add_file(filename=None, fmt = None, logger=None):
    if not logger:
        logger = get_logger()
    handler = logging.FileHandler(filename if filename else logger.name + ".log")
    handler.setFormatter(logging.Formatter(fmt if fmt else _def_fmt))
    logger.addHandler(handler)
    return handler

def log_add_console(fmt = None, logger=None):
    if not logger:
        logger = get_logger()
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt if fmt else _def_fmt))
    logger.addHandler(handler)
    return handler

def get_logger(name=None, level=logging.DEBUG):
    if name is None:
        name = _def_name

    if name in _logger_cache:
        return _logger_cache[name]

    log = logging.getLogger(name)
    _logger_cache[name] = log
    log.setLevel(level)
    return log



