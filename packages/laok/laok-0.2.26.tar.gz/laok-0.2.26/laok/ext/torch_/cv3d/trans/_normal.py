#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 11:31:57
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldNormalize']

class CldNormalize(object):
    def __call__(self, points):
        pc = points[:, 0:3]
        centroid = np.mean(pc, axis=0)
        pc = pc - centroid
        m = np.max(np.sqrt(np.sum(pc ** 2, axis=1)))
        pc = pc / m
        points[:, 0:3] = pc
        return points
