#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 20:23:13

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['save_onnx_model']

def save_onnx_model(model, input, filename, **kws):
    torch.onnx.export(model, input, filename, **kws)
