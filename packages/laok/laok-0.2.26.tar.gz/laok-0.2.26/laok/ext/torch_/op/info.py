#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/18 02:35:56

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
from laok.base.str import fmt_size
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['print_data']


def print_data(data, **kws):
    if isinstance(data, torch.TensorType):
        _print_tensor(data, **kws)
    elif isinstance(data, torch.Module):
        _print_model(data, **kws)

def _print_tensor(data, title=None, show_data=True):
    '''print detail data information
    '''

    if title is None:
        msg = f"===="
    else:
        msg = f"====[{title}] "

    if isinstance(data, torch.Tensor):
        _type = 'Tensor'
    else:
        _type = type(data)

    msg += f'type[{_type}]'
    if isinstance(data, torch.Tensor):
        msg += f' shape{fmt_size(data.shape)} dim[{data.ndim}] dtype[{_fmt_dtype(data.dtype)}] device[{data.device}]'

    msg += f' id[{id(data)}]\n'

    if show_data:
        msg += f'{data}'

    print(msg)
    return data

def _print_model(model):
    print(f'=== name: {model.__class__.__name__}')
    for i, (name, param) in enumerate(model.named_parameters()):
        print( f"<{i}> {name}")
        print( f"    requires_grad:{param.requires_grad}  size={fmt_size(param.size())}")
    return model

def _fmt_dtype(dt):
    return str(dt).replace('torch.', '')