#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 10:55:37
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldRandomDropout']

class CldRandomDropout:
    def __init__(self, max_dropout_ratio=0.875):
        assert max_dropout_ratio >= 0 and max_dropout_ratio < 1
        self.max_dropout_ratio = max_dropout_ratio

    def __call__(self, points):
        dropout_ratio = np.random.random() * self.max_dropout_ratio  # 0~0.875
        drop_idx = np.where(np.random.random((points.shape[0])) <= dropout_ratio)[0]
        if len(drop_idx) > 0:
            points[drop_idx] = points[0]  # set to the first point

        return points
