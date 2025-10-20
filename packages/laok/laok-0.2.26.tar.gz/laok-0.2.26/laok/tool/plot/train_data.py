#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/9 19:27:37

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import matplotlib.pyplot as plt
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['plot_acc', ]

def plot_acc(train_acc, test_acc, title='train and test accuracy', save_img_file=None, plt_show=True):
    epochs = list(range(1, len(train_acc) + 1))

    # 创建图形和坐标轴
    plt.figure(figsize=(10, 6))

    # 绘制训练准确率曲线
    train_line, = plt.plot(epochs, train_acc, label='train')
    max_train_idx = train_acc.index(max(train_acc))
    plt.annotate(f'max: {max(train_acc):.4f}',
                 xy=(epochs[max_train_idx], train_acc[max_train_idx]),
                 xytext=(epochs[max_train_idx]+0.1, train_acc[max_train_idx]+0.01),
                 # arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8)
                 )
    plt.scatter([epochs[max_train_idx]], [train_acc[max_train_idx]], color='red', s=50)

    # 绘制测试准确率曲线
    test_line, = plt.plot(epochs, test_acc,  label='test')
    max_test_idx = test_acc.index(max(test_acc))
    plt.annotate(f'max: {max(test_acc):.4f}',
                 xy=(epochs[max_test_idx], test_acc[max_test_idx]),
                 xytext=(epochs[max_test_idx]+0.1, test_acc[max_test_idx]+0.01),
                 # arrowprops=dict(facecolor='black', shrink=0.05, width=1.5, headwidth=8)
                 )
    plt.scatter([epochs[max_test_idx]], [test_acc[max_test_idx]], color='red', s=50)

    # 设置图表标题和坐标轴标签
    plt.title(title)
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    # plt.xticks(epochs)  # 设置x轴刻度为整数轮次
    plt.grid(True, linestyle='--', alpha=0.7)

    # 添加图例和显示图形
    plt.legend(handles=[train_line, test_line])
    plt.tight_layout()  # 确保标签和注释不会超出图形边界

    if save_img_file:
        plt.savefig(save_img_file)

    if plt_show:
        plt.show()