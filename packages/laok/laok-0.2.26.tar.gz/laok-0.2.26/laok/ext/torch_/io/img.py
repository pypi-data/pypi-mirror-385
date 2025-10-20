#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 21:34:10

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torchvision.transforms as TF
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['read_img_imagenet']

def read_img_imagenet(filename, resize=256, crop_size=224, mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
    from PIL import Image
    ts = TF.Compose([
        TF.Resize(resize),
        TF.CenterCrop(crop_size),
        TF.ToTensor(),
        TF.Normalize(mean=mean,std=std),
    ])
    img = Image.open(filename)
    return ts(img)

