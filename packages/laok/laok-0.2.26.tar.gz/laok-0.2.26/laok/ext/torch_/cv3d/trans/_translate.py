#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 10:54:40
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldTranslate']

class CldTranslate(object):
    def __init__(self, translate_range=0.1):
        self.translate_range = translate_range

    def __call__(self, points):
        translation = np.random.uniform(-self.translate_range, self.translate_range)
        points[:, 0:3] += translation
        return points
