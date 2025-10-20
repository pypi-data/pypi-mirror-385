#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/11/28 10:11:49

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import imagesize
# ===============================================================================
r'''
'''
# ===============================================================================
def get_size(img_file):
    '''返回 (w,h)
    '''
    return imagesize.get(img_file)

def get_dpi(img_file):
    '''返回 (x_dpi, y_dpi)
    '''
    return imagesize.getDPI(img_file)