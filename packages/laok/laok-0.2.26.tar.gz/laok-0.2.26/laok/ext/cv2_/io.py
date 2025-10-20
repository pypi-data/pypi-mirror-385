#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/11 14:36:36

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
import cv2
import numpy as np
from .cvt import swap_rb, keep_bgr, keep_gray
from .info import is_color, image_size
#===============================================================================
'''     
'''
#===============================================================================
__all__ = ['fix_cv_read',
           'read_image', 'read_color', 'read_gray',
           'write_image',
           'read_video', 'read_camera', 'VideoWriter',
           ]

####################    读取图像
def fix_cv_read():
    '''主要功能是修复 读取中文路径时候的问题,本质上就是替换 cv2.imread函数
    '''
    _org_read = cv2.imread
    cv2.imread = read_image

def read_image(filename, flags = cv2.IMREAD_COLOR):
    return cv2.imdecode(np.fromfile(filename, dtype=np.uint8), flags)

def read_color(filename, bgr=True):
    img = read_image(filename, cv2.IMREAD_COLOR)
    if not bgr:
        return swap_rb(img)
    return img

def read_gray(filename):
    return read_image(filename, cv2.IMREAD_GRAYSCALE)

def write_image(filename, data, params=None):
    name, ext = os.path.splitext(filename)
    retval, buf = cv2.imencode(ext, data, params)
    return buf.tofile(filename)

def write_jpg(filename, data, quality=95):
    return write_image(filename, data, [cv2.IMWRITE_JPEG_QUALITY, quality])

def write_png(filename, data, compression=1):
    return write_image(filename, data, [cv2.IMWRITE_PNG_COMPRESSION, compression])
####################    读取视频和相机
def _read_capture(fileOrId):
    try:
        cap = cv2.VideoCapture(fileOrId)
        while True:
            ret, frame = cap.read()
            if not ret:  # 如果正确读取帧，ret为True
                break
            yield frame
    finally:
        cap.release()

def read_video(video_file):
    yield from _read_capture(video_file)

def read_camera(camId = 0):
    yield from _read_capture(camId)


class VideoWriter:
    def __init__(self, filename, fourcc="mp4v", fps=24, frameSize=None, isColor=None):
        self.filename_ = filename
        self.frameSize_ = frameSize
        self.isColor_ = isColor
        self.fps_ = fps
        self.fourcc_ =  cv2.VideoWriter_fourcc(*fourcc)
        self.writer_ = None

    def _make_video(self, img):
        if self.frameSize_ is None:
            self.frameSize_ = image_size(img)

        if self.isColor_ is None:
            self.isColor_ = is_color(img)
        self.writer_ = cv2.VideoWriter(filename=self.filename_, fourcc=self.fourcc_,
                                      fps=self.fps_, frameSize=self.frameSize_, isColor=self.isColor_)

    def write(self, img):
        if self.writer_ is None:
            self._make_video(img)

        if self.isColor_ :
            img = keep_bgr(img)
        else:
            img = keep_gray(img)

        if image_size(img) != self.frameSize_:
            img = cv2.resize(img, dsize=(self.frameSize_[0], self.frameSize_[1]),
                             interpolation=cv2.INTER_LINEAR)
        self.writer_.write(img)

    def close(self):
        if self.writer_ is not None:
            self.writer_.release()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

