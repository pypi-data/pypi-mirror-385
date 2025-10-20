#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 20:23:23

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['save_jit_model', 'load_jit_model']

def save_jit_model(model, input, filename):
    if isinstance(model, torch.jit.TracedModule):
        traced_model = model
    else:
        try:
            mode = model.training
            model.eval()
            traced_model = torch.jit.trace(model, input)
        finally:
            model.train(mode)

    traced_model.save(filename)
    return traced_model

def load_jit_model(filename):
    ''' load trace model
    '''
    return torch.jit.load(filename)
