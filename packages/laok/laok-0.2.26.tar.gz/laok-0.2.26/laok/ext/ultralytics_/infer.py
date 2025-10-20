#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/12/6 23:15:46

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
import cv2
from ultralytics import YOLO
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ =['YoloDet', 'YoloSeg', ]

class YoloDet:
    def __init__(self, model_file, cls_file=None):
        self.setModel(model_file)
        self.setClsFile(cls_file)

    def setClsFile(self, cls_file):
        '''加载 名字索引文件
        '''
        self.nameIdx = laok.NameIndexFile(cls_file)

    def setModel(self, model_file):
        '''设置模型文件 .pt
        '''
        self.model = YOLO(model_file)

    def predict(self, img, conf_threshold=0.3, verbose=False):
        '''执行推理  cv2格式
        '''
        results = self.model.predict(img, verbose=verbose)
        # laok.dump(self.model.predictor)
        result = results[0]  # 单个图片, batch=1

        res = []
        for i, box in enumerate(result.boxes):
            conf = box.conf.cpu().item()
            if conf < conf_threshold:
                continue
            cls = box.cls.cpu().item()
            x1, y1, x2, y2 = box.xyxy.cpu().flatten().tolist()
            name = self.nameIdx.getName(cls)
            res.append({
                "conf": conf,
                "cls": int(cls),
                "name": name,
                "rect": [x1, y1, x2-x1, y2-y1]
                })
        return res


class YoloSeg:
    def __init__(self, model_file, cls_file=None):
        self.setModel(model_file)
        self.setClsFile(cls_file)

    def setClsFile(self, cls_file):
        '''加载 名字索引文件
        '''
        self.nameIdx = laok.NameIndexFile(cls_file)

    def setModel(self, model_file):
        '''设置模型文件 .pt
        '''
        self.model = YOLO(model_file)

    def predict(self, img, conf_threshold=0.3, verbose=False):
        '''执行推理  cv2格式
        '''
        results = self.model.predict(img, verbose=verbose)
        result = results[0]  # 单个图片, batch=1

        res = []
        for i, box in enumerate(result.boxes):
            conf = box.conf.cpu().item()
            if conf < conf_threshold:
                continue

            cls = box.cls.cpu().item()
            name = self.nameIdx.getName(cls)

            x1, y1, x2, y2 = box.xyxy.cpu().flatten().tolist()

            mask = result.masks[i].data[0].cpu().numpy()

            im0_shape = result.orig_shape
            mask = cv2.resize(mask, (im0_shape[1], im0_shape[0]), interpolation=cv2.INTER_LINEAR)  # INTER_CUBIC would be better

            res.append({
                "conf": conf,
                "cls": int(cls),
                "name": name,
                "rect": [x1, y1, x2-x1, y2-y1],
                "mask": mask,
                })
        return res