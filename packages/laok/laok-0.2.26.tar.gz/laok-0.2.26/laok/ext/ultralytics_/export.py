#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/11 12:35:20

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
import shutil
import ultralytics
from functools import partial
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['export_onnx', 'export_onnx_yolo', 'export_onnx_yolo_sam', 'export_onnx_yolo_sam2',
           'export_onnx_yolo_sam_mobile', 'export_onnx_yolo_sam_fast',
           'export_onnx_yolo_nas', 'export_onnx_rt_detr',
           'export_onnx_yolo_world', 'export_onnx_yolo_e'
           ]

def export_onnx(src_file, imgsz, dst_file=None, cls_name='YOLO', **kws):
    '''
    opset = 12, dynamic=False, 用于支持 opencv-dnn
    '''
    cls = getattr(ultralytics, cls_name)
    model = cls(src_file)

    kws['imgsz'] = imgsz
    kws['format'] = kws.pop('format', 'onnx')
    kws['opset'] = kws.pop('opset', 12)
    kws['dynamic'] = kws.pop('dynamic', False)

    print('export args:', kws)
    model.export(**kws)
    if dst_file:
        onnx_model = laok.path_replace_ext(src_file, 'onnx')
        shutil.copy(onnx_model, dst_file)

export_onnx_yolo = export_onnx
export_onnx_yolo_sam = partial(export_onnx, cls_name='SAM')
export_onnx_yolo_sam2 = partial(export_onnx, cls_name='SAM')
export_onnx_yolo_sam_mobile = partial(export_onnx, cls_name='SAM')
export_onnx_yolo_sam_fast = partial(export_onnx, cls_name='FastSAM')
export_onnx_yolo_nas = partial(export_onnx, cls_name='NAS')
export_onnx_rt_detr = partial(export_onnx, cls_name='RTDETR', opset=16)
export_onnx_yolo_world = partial(export_onnx, cls_name='YOLOWorld')
export_onnx_yolo_e = partial(export_onnx, cls_name='YOLOE')



