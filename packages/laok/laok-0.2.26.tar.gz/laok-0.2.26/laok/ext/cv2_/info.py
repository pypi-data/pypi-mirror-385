#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/11 15:40:10

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''

# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['is_color', 'is_gray',
           'image_size', 'image_width',
           'image_height', 'image_center',
           'image_channels']

def is_color(img):
    return img.ndim == 3 and img.shape[-1] > 1

def is_gray(img):
    return not is_color(img)

def image_size(img):
    '''width, height'''
    return (img.shape[1], img.shape[0])

def image_width(img):
    return img.shape[1]

def image_height(img):
    return img.shape[0]

def image_center(img):
    height, width = img.shape[0:2]
    return (width//2, height//2)

def image_channels(img):
    if img.ndim == 2:
        return 1
    if img.ndim == 3:
        return img.shape[-1]
    assert("error img format")

