#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/11 15:34:31

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
from .info import is_gray, is_color, image_size
# ===============================================================================
r'''# Opencv  图像格式        通道：BGR 像素值：[0,255]        (h,w)
    gray是 (h,w)  
    color是(h,w,3)
cv2.INTER_LINEAR  = 1
'''
# ===============================================================================
__all__ = [ 'gray2bgr', 'gray2rgb',
            'bgr2gray', 'rgb2gray',
            'swap_rb',
            'keep_bgr', 'keep_gray',
            'resize_abs', 'resize_rel'
           ]

def gray2bgr(img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    return img

def gray2rgb(img):
    if img.ndim == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img

def bgr2gray(img):
    if img.ndim == 3:
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        elif img.shape[-1] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    return img

def rgb2gray(img):
    if img.ndim == 3:
        if img.shape[-1] == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        elif img.shape[-1] == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
    return img

def swap_rb(img):
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def norm_minmax_u8(mat, alpha=0, beta=255):
    return cv2.normalize(mat, dst=None, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

def norm_minmax_f32(mat, alpha=0, beta=1):
    return cv2.normalize(mat, dst=None, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)

def norm_minmax_i32(mat, alpha=0, beta=255):
    return cv2.normalize(mat, dst=None, alpha=alpha, beta=beta, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32S)

def keep_gray(img):
    if is_color(img):
        return bgr2gray(img)
    return img

def keep_bgr(img):
    if is_gray(img):
        return gray2bgr(img)
    return img

def resize_abs(img, width, height=0, interpolation=cv2.INTER_LINEAR):
    if height == 0:
        height = width
    return cv2.resize(img, dsize=(int(width), int(height)), interpolation=interpolation)

def resize_rel(img, fx=0.5, fy=0, interpolation=cv2.INTER_LINEAR):
    if fy == 0:
        fy = fx
    return cv2.resize(img, fx=fx, fy=fy, interpolation=interpolation)

