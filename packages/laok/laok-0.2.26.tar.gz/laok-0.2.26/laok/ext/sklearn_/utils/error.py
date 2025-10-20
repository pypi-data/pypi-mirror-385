#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 23:29:56

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import metrics
# ===============================================================================
r'''误差计算
'''
# ===============================================================================
__all__ = ['error_coverage',
 'error_max',
 'error_mean_absolute',
 'error_mean_absolute_percentage',
 'error_mean_squared',
 'error_mean_squared_log',
 'error_median_absolute']



error_coverage = metrics.coverage_error
error_max = metrics.max_error
error_mean_absolute = metrics.mean_absolute_error
error_mean_absolute_percentage = metrics.mean_absolute_percentage_error
error_mean_squared = metrics.mean_squared_error
error_mean_squared_log = metrics.mean_squared_log_error
error_median_absolute = metrics.median_absolute_error

