#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/3/7 17:34:59

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
#
#===============================================================================
__all__ = ['cld_bounding_box']


def cld_bounding_box(cld):
    minv = np.min(cld, axis=0)
    maxv = np.max(cld, axis=0)
    return (minv[0:3], maxv[0:3])

