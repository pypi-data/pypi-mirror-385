#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 19:38:18

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import matplotlib.pyplot as plt
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['font_support_chinese']

def font_support_chinese():
    plt.rcParams['font.family']=["SimHei", "sans-serif"] # 黑体支持中文
    plt.rcParams['axes.unicode_minus'] = False # 解决负号显示问题
