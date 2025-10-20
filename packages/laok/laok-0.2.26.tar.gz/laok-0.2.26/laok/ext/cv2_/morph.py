#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 21:47:37

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['morph_open', 'morph_close',
           'morph_erode', 'morph_dilate',
           'morph_gradient', 'morph_hitmiss',
           'morph_tophat', 'morph_blackhat',
           'kernel_rect', 'kernel_cross', 'kernel_ellipse',
]

def kernel_rect(ksize=(3, 3)):
    return cv2.getStructuringElement(shape=cv2.MORPH_RECT, ksize=ksize)

def kernel_cross(ksize=(3, 3)):
    return cv2.getStructuringElement(shape=cv2.MORPH_CROSS, ksize=ksize)

def kernel_ellipse(ksize=(3, 3)):
    return cv2.getStructuringElement(shape=cv2.MORPH_ELLIPSE, ksize=ksize)

def morph_open(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_OPEN, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_close(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_CLOSE, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_erode(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_ERODE, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_dilate(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_DILATE, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_gradient(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_GRADIENT, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_tophat(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_TOPHAT, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_blackhat(img, kernel=None, iterations=1, borderType=cv2.BORDER_CONSTANT, borderValue=(0,0,0)):
    return cv2.morphologyEx(img, op=cv2.MORPH_BLACKHAT, kernel=kernel, iterations=iterations, borderType=borderType, borderValue=borderValue)

def morph_hitmiss(img, kernel=None, iterations=1):
    return cv2.morphologyEx(img, op=cv2.MORPH_HITMISS, kernel=kernel, iterations=iterations)
