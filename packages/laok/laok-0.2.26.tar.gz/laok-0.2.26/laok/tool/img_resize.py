#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 19:43:53

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
import laok.ext.cv2_ as cv2_
import imagesize
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['resize_to_width_under',
            'resize_to_height_under',
            'resize_abs_under',
           'resize_rel_under',
           ]

def resize_to_width_under(img_dir, w, interpolation=1):
    for img_file in laok.image_under(img_dir):
        w2, h2 = imagesize.get(img_file)
        if w2 == w:
            continue
        img = cv2_.read_image(img_file)
        img = cv2_.resize_to_width(img, w, interpolation)
        cv2_.write_image(img_file, img)
        print(f'resize file:{img_file}')

def resize_to_height_under(img_dir, h, interpolation=1):
    for img_file in laok.image_under(img_dir):
        w2, h2 = imagesize.get(img_file)
        if h2 == h:
            continue
        img = cv2_.read_image(img_file)
        img = cv2_.resize_to_height(img, h, interpolation)
        cv2_.write_image(img_file, img)
        print(f'resize file:{img_file}')
def resize_abs_under(img_dir, w, h, interpolation=1):
    for img_file in laok.image_under(img_dir):
        w2, h2 = imagesize.get(img_file)
        if w2 == w and h2 == h:
            continue
        img = cv2_.read_image(img_file)
        img = cv2_.resize_abs(img, w, h, interpolation)
        cv2_.write_image(img_file, img)
        print(f'resize file:{img_file}')
def resize_rel_under(img_dir, rw, rh, interpolation=1):
    for img_file in laok.image_under(img_dir):
        img = cv2_.read_image(img_file)
        img = cv2_.resize_rel(img, rw, rh, interpolation)
        cv2_.write_image(img_file, img)
        print(f'resize file:{img_file}')