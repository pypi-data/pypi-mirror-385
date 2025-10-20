#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 16:58:45

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import math
import matplotlib.pyplot as plt
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['show_image',
           'show_image_list',
           'show_regression',
           'show_clusters']

def show_image(img, label=None, img_kws=None, is_opencv=False, **plt_kws):
    '''显示图像
    '''
    fig, axes = plt.subplots(**plt_kws)

    if label:
        axes.set_title(label)

    if img_kws is None:
        img_kws = {}

    if is_opencv:
        if img.ndim == 2:
            img_kws.setdefault('cmap', 'gray')
        if img.ndim == 3:
            # im_swap = img.copy()
            # im_swap[:, :, 0], im_swap[:, :, 2] = img[:, :, 2], img[:, :, 0]
            img = img[:, :, ::-1]

    axes.imshow(img, **img_kws)

    axes.get_xaxis().set_visible(False) #隐藏x轴
    axes.get_yaxis().set_visible(False) #隐藏y轴

    plt.show()


def show_image_list(images, labels=None, ncols=1, img_kws=None, is_opencv=False, **plt_kws):
    '''显示多张图片
    '''
    nrows = int( math.ceil(len(images) / ncols) )
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, **plt_kws)

    axes.resize(nrows * ncols)
    if img_kws is None:
        img_kws = {}

    for i, f in enumerate(axes):
        if i < len(images):

            img = images[i]
            if is_opencv:
                if img.ndim == 2:
                    img_kws.setdefault('cmap', 'gray')
                if img.ndim == 3:
                    # img = img[:, :, [2,1,0]]
                    img = img[:, :, ::-1]

            f.imshow(img, **img_kws)

            if labels and i < len(labels):
                f.set_title(labels[i])
        else:
            f.spines['top'].set_visible(False)
            f.spines['right'].set_visible(False)
            f.spines['bottom'].set_visible(False)
            f.spines['left'].set_visible(False)

        f.get_xaxis().set_visible(False)
        f.get_yaxis().set_visible(False)

    plt.show()


def show_regression(X_test, y_test, y_pred, title=None):
    '''显示 数据点 和 回归线条,只支持显示1维数据
    '''
    plt.scatter(X_test, y_test, color="black")
    plt.plot(X_test, y_pred, color="blue", linewidth=3)
    if title:
        plt.title(title)
    plt.show()


def show_clusters(X, labels, indexes=(0, 1)):
    '''显示 类别
    '''
    clusters = np.unique(labels)
    x, y = indexes
    for cluster in clusters:
        row_ix = np.where(labels == cluster)
        plt.scatter(X[row_ix, x], X[row_ix, y])
    plt.show()