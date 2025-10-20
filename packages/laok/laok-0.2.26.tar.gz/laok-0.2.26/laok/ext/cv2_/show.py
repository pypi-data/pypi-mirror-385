#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/11 19:26:54

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['show_image', 'wait_key']

def show_image(mat, winname='img',
               winflag = cv2.WINDOW_NORMAL,
               title = ""):

    #窗口名字
    cv2.namedWindow(winname, winflag)

    # 标题
    if title:
        cv2.setWindowTitle(winname, title)

    if mat.dtype == bool: #转换bool 类型
        mat = mat.astype(np.uint8) * 255
    elif mat.dtype != np.uint8:  # 转换 其它类型
        mat = cv2.normalize(mat, None, alpha=0, beta=255,
                            norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)

    cv2.imshow(winname, mat)

def wait_key(wait_delay=0):
    '''支持 Esc 退出
    '''
    key = cv2.waitKey(wait_delay)
    if key & 0xFF == 27:  # 'Esc' to quit
        exit()
    return key