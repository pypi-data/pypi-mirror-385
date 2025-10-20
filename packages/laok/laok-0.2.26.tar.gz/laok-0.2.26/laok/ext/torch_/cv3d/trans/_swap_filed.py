#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/6/16 16:00:28

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['CldSwapField']

class CldSwapField:
    def __init__(self, field_list):
        self.field_list = field_list

    def __call__(self, points):
        points[:, :] = points[:, self.field_list]
        return points

