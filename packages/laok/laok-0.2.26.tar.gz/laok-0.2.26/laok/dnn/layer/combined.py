#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/13 11:45:36

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
from laok import kws_merge
import torch.nn as nn
# ===============================================================================
r'''
Conv → Batch Norm → Activate Function
    这是最为常见的组合顺序，广泛应用于众多经典网络架构，像 ResNet 就采用了这种方式。
    原理剖析：卷积操作之后，运用批量归一化对数据分布加以调整，接着再通过激活函数引入非线性因素。
    优势所在：能有效缓解梯度消失问题，使网络的训练过程更加稳定，还可加快模型的收敛速度。
    适用场景：适合大多数的深度学习任务，特别是在图像分类任务中表现出色。
'''
# ===============================================================================
__all__ = ['Conv1BatchRelu']

class _ConvNormActivate(nn.Module):
    def __init__(self, conv_cls=None, conv_kws=None, norm_cls=None, norm_kws=None, act_cls=None, act_kws=None):
        super().__init__()
        self.conv = conv_cls(**kws_merge(conv_kws))
        self.bn = norm_cls(**kws_merge(norm_kws))
        self.activation = act_cls(**kws_merge(act_kws))

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.activation(x)
        return x

class Conv1BatchRelu(_ConvNormActivate):
    def __init__(self, in_channels, out_channels, kernel_size=1, conv_kws=None, norm_kws=None, act_kws=None):
        conv_kws = kws_merge(conv_kws, in_channels=in_channels, out_channels=out_channels, kernel_size=kernel_size)
        norm_kws = kws_merge(norm_kws, num_features=out_channels)
        act_kws = kws_merge(act_kws, inplace=True)
        super().__init__(conv_cls = nn.Conv1d, norm_cls = nn.BatchNorm1d, act_cls = nn.ReLU,
                         conv_kws = conv_kws, norm_kws = norm_kws, act_kws = act_kws)



















