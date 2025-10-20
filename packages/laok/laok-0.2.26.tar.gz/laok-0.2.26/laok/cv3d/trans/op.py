#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/9 19:43:59

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['apply_batch', 'apply_sample_point', 'apply_sample_points', 'mat_angle_axis', 'plane_symm']

def apply_batch(batch_data, trans):
    B = batch_data.shape[0]
    for k in range(B):
        batch_data[k, ...] = trans(batch_data[k, ...])
    return batch_data

def apply_sample_points(points, trans, ratio=0.8):
    sample_ratio = np.random.random() * ratio
    drop_idx = np.where(np.random.random((points.shape[0])) <= sample_ratio)[0]
    if len(drop_idx) > 0:
        points[drop_idx] = trans(points[drop_idx])
    return points

def apply_sample_point(points, trans, ratio=0.8):
    sample_ratio = np.random.random() * ratio
    drop_idx = np.where(np.random.random((points.shape[0])) <= sample_ratio)[0]
    for idx in drop_idx:
        points[idx] = trans(points[idx])
    return points

def mat_angle_axis(angle: float, axis: np.ndarray):
    u = axis / np.linalg.norm(axis)
    cosval, sinval = np.cos(angle), np.sin(angle)
    # yapf: disable
    cross_prod_mat = np.array([[0.0, -u[2], u[1]],
                               [u[2], 0.0, -u[0]],
                               [-u[1], u[0], 0.0]])

    R = cosval * np.eye(3) + sinval * cross_prod_mat + (1.0 - cosval) * np.outer(u, u)
    # yapf: enable
    return R

def plane_symm(points, a=0, b=0, c=0, d=0):
    if a == 0 and b == 0 and c == 0:
        a = 0.0001
    if len(points.shape) > 1:
        lam = ((a * points[:, 0] + b * points[:, 1] + c * points[:, 2] + d) / (a * a + b * b + c * c))
        points[:, 0] -= 2 * lam * a
        points[:, 1] -= 2 * lam * b
        points[:, 2] -= 2 * lam * c
    else:
        lam = ((a * points[0] + b * points[1] + c * points[2] + d) / (a * a + b * b + c * c))
        points[0] -= 2 * lam * a
        points[1] -= 2 * lam * b
        points[2] -= 2 * lam * c
    return points
