#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 10:52:27
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldScale']

class CldScale(object):
    def __init__(self, lo=0.8, hi=1.25):
        self.lo, self.hi = lo, hi

    def __call__(self, points):
        scaler = np.random.uniform(self.lo, self.hi)
        points[:, 0:3] *= scaler
        return points
