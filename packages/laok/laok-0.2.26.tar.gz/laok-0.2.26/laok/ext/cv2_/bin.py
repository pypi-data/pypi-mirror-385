#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 15:29:37

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ =['bin_otsu', 'bin_triangle', 'bin_mean',
          'bin_threshold',
          'bin_adapt_mean', 'bin_adapt_gauss']

def bin_otsu(img, scale=1.0, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    th, ret = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU + flag)
    if scale == 1.0:
        return ret
    th, ret = cv2.threshold(img, th*scale, 255, flag)
    return ret

def bin_triangle(img, scale=1.0, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    th, ret = cv2.threshold(img, 0, 255, cv2.THRESH_TRIANGLE + flag)
    if scale == 1.0:
        return ret
    th, ret = cv2.threshold(img, th*scale, 255, flag)
    return ret

def bin_mean(img, scale=1.0, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    value = cv2.mean(img)
    th, ret = cv2.threshold(img, value[0]*scale, 255, flag)
    return ret

def bin_threshold(img, value=128, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    th, ret = cv2.threshold(img, value, 255, flag)
    return ret

def bin_adapt_mean(img, blockSize=11, C=2, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    return cv2.adaptiveThreshold(img, maxValue=255,
                                 adaptiveMethod=cv2.ADAPTIVE_THRESH_MEAN_C,
                                 thresholdType=flag, blockSize=blockSize, C=C)

def bin_adapt_gauss(img, blockSize=11, C=2, inv=False):
    flag = cv2.THRESH_BINARY_INV if inv else cv2.THRESH_BINARY
    return cv2.adaptiveThreshold(img, maxValue=255,
                                 adaptiveMethod=cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 thresholdType=flag, blockSize=blockSize, C=C)


