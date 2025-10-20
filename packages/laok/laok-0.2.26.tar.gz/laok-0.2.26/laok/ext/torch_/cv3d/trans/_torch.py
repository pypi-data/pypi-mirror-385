#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/25 11:04:43
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['CldToTensor']

class CldToTensor(object):
    def __call__(self, points):
        import torch
        return torch.from_numpy(points).float()
