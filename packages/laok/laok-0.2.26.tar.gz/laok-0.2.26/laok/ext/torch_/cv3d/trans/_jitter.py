#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 10:53:29
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldJitter']

class CldJitter:
    def __init__(self, std=0.01, clip=0.05):
        self.std, self.clip = std, clip

    def __call__(self, points):
        jittered_data = np.random.normal(0.0, self.std, (points.shape[0], 3) )
        jittered_data = np.clip(jittered_data, -self.clip, self.clip)
        points[:, 0:3] += jittered_data
        return points
