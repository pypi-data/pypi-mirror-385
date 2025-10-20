#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 20:24:46

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['filter_2d',  'filter_median', 'filter_box', 'filter_gauss',
            'filter_bilateral'
]

def filter_2d(img, kernel, delta=0, borderType=cv2.BORDER_REPLICATE):
    return cv2.filter2D(img, ddepth=-1, kernel=kernel, delta=delta, borderType=borderType)

def filter_median(img, ksize=3):
    return cv2.medianBlur(img, ksize=ksize)

def filter_box(img, ksize=(3,3), borderType=cv2.BORDER_REPLICATE ):
    return cv2.boxFilter(img, ddepth=-1, ksize=ksize, normalize=True, borderType=borderType)

def filter_gauss(img, ksize=(3,3), sigmaX=0, sigmaY=0, borderType=cv2.BORDER_REPLICATE):
    return cv2.GaussianBlur(img, ksize=ksize, sigmaX=sigmaX, sigmaY=sigmaY, borderType=borderType)

def filter_bilateral(img, d=5, sigmaColor=30, sigmaSpace=30, borderType=cv2.BORDER_REPLICATE):
    return cv2.bilateralFilter(img, d=d, sigmaColor=sigmaColor, sigmaSpace=sigmaSpace, borderType=borderType)




