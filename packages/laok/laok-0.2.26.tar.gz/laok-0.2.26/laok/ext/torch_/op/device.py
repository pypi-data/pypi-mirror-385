#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 16:20:56
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['get_device', 'set_device']

def get_device(obj=None):
    '''自动获取对象的设备类型
    :param obj: 对象
    :return:
    '''
    if obj is None:
        obj = "cuda" if torch.cuda.is_available() else "cpu"

    if isinstance(obj, str):
        return torch.device(obj)

    if isinstance(obj, torch.Tensor):
        return obj.device

    if isinstance(obj, torch.nn.Module):
        p = next(obj.parameters())
        return p.device

    if isinstance(obj, torch.device):
        return obj

def set_device(src, dst):
    device = get_device(dst)
    return src.to(device)
