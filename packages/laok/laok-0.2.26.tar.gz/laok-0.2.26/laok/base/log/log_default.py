#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 22:34:15
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from .log import get_logger
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['log_debug', 'log_info', 'log_warning', 'log_error', 'log_critical']

#默认日志
_logger = get_logger()

# 日志函数
log_debug = _logger.debug
log_info = _logger.info
log_warning = _logger.warning
log_error = _logger.error
log_critical = _logger.critical
