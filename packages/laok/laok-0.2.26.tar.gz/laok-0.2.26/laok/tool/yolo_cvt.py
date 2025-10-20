#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/11/27 20:59:23

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
import imagesize
# ===============================================================================
r'''
'''
# ===============================================================================

def _box_to_yolo(w, h, xmin, ymin, xmax, ymax):
    dw = 1. / w
    dh = 1. / h
    cx = ( (xmin + xmax) / 2.0 )*dw
    cy = ( (ymin + ymax) / 2.0 )*dh
    rw = (xmax - xmin) * dw
    rh = (ymax - ymin) * dh
    return cx, cy, rw, rh

def rect_to_yolo(data_dir):
    for img_file in laok.image_under(data_dir):
        imgsz = imagesize.get(img_file)
        w, h = imgsz
        txt_file = laok.path_replace_ext(img_file, 'txt')
        need_cvt = True
        data_list = []
        for line in laok.file_read_lines(txt_file):
            tp, x1, y1, w1, h1 = line.split()
            x1, y1 = int(x1), int(y1)
            if x1 >= 1:
                need_cvt = False
                break
            x2, y2 = x1 + int(w1), y1 + int(h1)
            cx, cy, rw, rh = _box_to_yolo(w, h, x1, y1, x2, y2)
            data_list.append("{} {} {} {} {}".format(tp, cx, cy, rw, rh))

        if need_cvt:
            laok.file_write_lines(txt_file, data_list)





data_dir = r'C:\Users\k\Desktop\Image'
rect_to_yolo(data_dir)