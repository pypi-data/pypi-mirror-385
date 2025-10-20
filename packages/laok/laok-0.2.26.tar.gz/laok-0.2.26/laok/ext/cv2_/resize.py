#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 19:30:19

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
from .info import image_size
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['resize_rel',
           'resize_abs', 'resize_to_width', 'resize_to_height',
           ]

def resize_rel(img, rw=0, rh=0, interpolation=cv2.INTER_LINEAR):
    if rw == 0 and rh == 0:
        return img
    if rw == 0:
        rw = rh
    if rh == 0:
        rh = rw
    return cv2.resize(img, fx=rw, fy=rh, interpolation=interpolation)

def resize_abs(img, w=0, h=0, interpolation=cv2.INTER_LINEAR):
    w, h = int(w), int(h)
    w2, h2 = image_size(img)
    if w == 0 and h == 0:
        return img
    if w == w2 and h == h2:
        return img
    if w == 0:
        w = w2
    if h == 0:
        h = h2
    return cv2.resize(img, dsize=(w, h), interpolation=interpolation)

def resize_to_width(img, w, interpolation=cv2.INTER_LINEAR):
    w2, h2 = image_size(img)
    h = w / w2 * h2
    return resize_abs(img, w, h, interpolation)

def resize_to_height(img, h, interpolation=cv2.INTER_LINEAR):
    w2, h2 = image_size(img)
    w = h / h2 * w2
    return resize_abs(img, w, h, interpolation)

