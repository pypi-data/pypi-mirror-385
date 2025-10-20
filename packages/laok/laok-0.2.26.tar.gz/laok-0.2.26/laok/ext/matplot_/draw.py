#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 17:28:03

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import matplotlib.pyplot as plt
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = [
    'draw_bar',
    'draw_bar_h',
    'draw_barbs',
    'draw_boxplot',
    'draw_contour',
    'draw_errorbar',
    'draw_event',
    'draw_fill',
    'draw_fill_between',
    'draw_fill_between_x',
    'draw_hexbin',
    'draw_hist',
    'draw_image',
    'draw_line',
    'draw_pie',
    'draw_polar',
    'draw_quiver',
    'draw_scatter',
    'draw_stack',
    'draw_stem',
    'draw_step',
    'draw_text',
    'draw_violin',
    'draw_xcoor',
]

draw_bar = plt.bar              # 垂直柱形图
draw_bar_h = plt.barh           # 水平条形图

draw_barbs = plt.barbs

draw_boxplot = plt.boxplot  # 箱型图

draw_contour = plt.contour

draw_errorbar = plt.errorbar

draw_event = plt.eventplot

draw_fill = plt.fill

draw_fill_between = plt.fill_between

draw_fill_between_x = plt.fill_betweenx

draw_hexbin = plt.hexbin

draw_hist = plt.hist            # 直方图

draw_hist2d = plt.hist2d        # 2D直方图

draw_image = plt.imshow         # 画图

draw_line = plt.plot            # 线条

draw_pie = plt.pie              # 饼图

draw_polar = plt.polar        # 极坐标图

draw_quiver = plt.quiver    # 二维箭头图

draw_scatter = plt.scatter      # 绘制x与y的散点图

draw_stack = plt.stackplot  # 绘制堆叠图

draw_stem = plt.stem    # 针状图（又称为“火柴图”）

draw_step = plt.step    # 阶梯图

draw_text = plt.text    # 文字

draw_violin = plt.violinplot

draw_xcoor = plt.xcorr


# import laok; laok.dump_module_all(preffix='draw_')
