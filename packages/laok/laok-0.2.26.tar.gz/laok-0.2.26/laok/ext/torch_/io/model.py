#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 20:30:40

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['save_model', 'save_model_params', 'load_model', 'load_model_params', 'load_model_params_obj']

def save_model(model, filename):
    torch.save(model, filename)
    return model

def save_model_params(model, filename):
    torch.save(model.state_dict(), filename)
    return model

def load_model(filename, map_location=None):
    return torch.load(filename, map_location=map_location)

def load_model_params(model, filename, map_location=None):
    _obj = load_model(filename, map_location=map_location)
    return load_model_params_obj(model, _obj)

def load_model_params_obj(model, data):
    if isinstance(data, torch.nn.Module):
        state = data.state_dict()
    else:
        state = data

    # 加载匹配的部分
    _model_state = model.state_dict()
    part_load = {}
    for k,v in state.items():
        if k in _model_state and _model_state[k].shape == v.shape:
            part_load[k] = v
    _model_state.update(part_load)
    model.load_state_dict(_model_state)

    return model