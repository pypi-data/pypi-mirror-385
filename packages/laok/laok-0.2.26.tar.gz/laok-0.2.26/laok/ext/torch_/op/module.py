#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 23:00:20

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
import laok
from .device import get_device
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['model_set_grad_by_name', 'model_set_grad_by_index',
           'inplace_relu', 'model_inplace_relu']

def model_set_grad_by_name(model, name_list, grad=False, show_info=False):
    if isinstance(name_list, str):
        name_list = [name_list]

    for name in name_list:
        if hasattr(model, name):
            module = getattr(model, name)

            if isinstance(module, torch.nn.Module):
                if show_info:
                    laok.log_info(f'freeze {name}')

                for n,p in module.named_parameters():
                    p.requires_grad = grad
                    if show_info:
                        laok.log_info(f'  freeze {n}')
        else:
            laok.log_error(f'no name:{name}')

    return model

def model_set_grad_by_index(model, index_list, grad=False, show_info=False):

    if isinstance(index_list, int):
        index_list = [index_list]

    for i, (n,p) in enumerate(model.named_parameters()):

        if i in index_list:
            p.requires_grad = grad

            if show_info:
                laok.log_info(f'freeze index:{i} name:{n}')

    return model

def inplace_relu(layer):
    classname = layer.__class__.__name__
    if classname.find('ReLU') != -1:
        layer.inplace=True

def model_inplace_relu(model):
    model.apply(inplace_relu)


