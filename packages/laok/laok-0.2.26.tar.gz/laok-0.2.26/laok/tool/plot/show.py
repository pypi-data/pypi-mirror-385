#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/10/11 12:13:52

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import matplotlib.pyplot as plt
# ===============================================================================
r'''
'''
# ===============================================================================

def show_tsne(features, labels, **tsne_kws):
    from sklearn.manifold import TSNE  # 从sklearn导入t-SNE算法

    # 使用t-SNE降维到2维
    n_components = tsne_kws.pop('n_components', 2)  # 降维到2维
    perplexity = tsne_kws.pop('perplexity', 30)  # 困惑度为30(控制局部和全局结构的平衡)通常建议值在5-50之间
    max_iter = tsne_kws.pop('max_iter', 300)  # 最大迭代300次
    random_state = tsne_kws.pop('random_state', 42) # 随机种子42
    tsne = TSNE(n_components=n_components,
                perplexity=perplexity,
                max_iter=max_iter,
                random_state=random_state, **tsne_kws)

    features_low = tsne.fit_transform(features)

    # 绘制二维t-SNE图
    # 创建散点图：x,y轴为降维后的两个维度, 颜色根据标签区分,使用viridis颜色映射, 透明度0.7, 点大小30
    scatter = plt.scatter(features_low[:, 0], features_low[:, 1], c=labels,
                          cmap='viridis', alpha=0.7, s=30)
    # 添加图例和标题
    plt.legend(*scatter.legend_elements(), title="Classes")  # 添加图例
    plt.title('t-SNE Visualization')  # 标题
    plt.xlabel('t-SNE dim 1')  # x轴标签
    plt.ylabel('t-SNE dim 2')  # y轴标签
    plt.colorbar(scatter, label='Class')  # 添加颜色条
    plt.grid(True, alpha=0.3)  # 添加半透明网格
    plt.show()