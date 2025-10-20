#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/28 11:49:47
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
#===============================================================================
r'''
'''
#===============================================================================
def farthest_point_sample_faster(pts: np.array, num: int) -> np.array:
    """
    Input:
        xyz: pointcloud data, [B, N, 3]
        npoint: number of samples
    Return:
        centroids: sampled pointcloud index, [B, npoint]
    """
    pc1 = np.expand_dims(pts, axis=0)   # 1, N, 3
    batchsize, npts, dim = pc1.shape
    # centroids 是当前点集中最远点的坐标集合, shape (B, N) -> (1, 300)  300时要采样的点数
    centroids = np.zeros((batchsize, num), dtype=np.long)
    # 距离的shape是 (B, ndataset) ndataset是输入点的数量
    distance = np.ones((batchsize, npts)) * 1e10
    # 初始化的最远点, 随机选取id, 如果batchsize不是1, 那就选取 batchsize个,
    farthest_id = np.random.randint(0, npts, (batchsize,), dtype=np.long)
    # batch_indices=[0,1,...,batchsize-1]
    batch_index = np.arange(batchsize)
    for i in range(num):
    # 更新第i个最远点的id, 这里时所有的batch都同时更新, farthest的维度和 centroids[:, i]的维度相同
        centroids[:, i] = farthest_id
    # 取出这个最远点的xyz坐标, 按维度分别取 batch\\点的id\\点的坐标, 然后view变换维度
        centro_pt = pc1[batch_index, farthest_id, :].reshape(batchsize, 1, 3)
    # 计算点集中的所有点到这个最远点的欧式距离
        # 等价于torch.sum((xyz - centroid) ** 2, 2)
        dist = np.sum((pc1 - centro_pt) ** 2, -1)
    # 更新distances，记录样本中每个点距离所有已出现的采样点的最小距离
        mask = dist < distance
    # 从更新后的distances矩阵中找出距离最远的点，作为最远点用于下一轮迭代
        distance[mask] = dist[mask]
        farthest_id = np.argmax(distance[batch_index])
    # 返回采样点的id
    return centroids