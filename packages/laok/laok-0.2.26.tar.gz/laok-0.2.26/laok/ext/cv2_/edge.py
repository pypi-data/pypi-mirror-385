#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 22:12:50

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['edge_sobel_x', 'edge_sobel_y', 'edge_sobel',
            'edge_scharr_x', 'edge_scharr_y', 'edge_scharr',
           'edge_laplace', 'edge_canny',
]

def edge_sobel_x(img):
    pass

def edge_sobel_y(img):
    pass

def edge_sobel(img):
    pass

def edge_scharr_x(img):
    pass

def edge_scharr_y(img):
    pass

def edge_scharr(img):
    pass

def edge_laplace(img):
    pass

def edge_canny(img, minVal=50, maxVal=150, apertureSize=3, L2gradient=False):
    return cv2.Canny(img, threshold1=minVal, threshold2=maxVal, apertureSize=apertureSize, L2gradient=L2gradient)


