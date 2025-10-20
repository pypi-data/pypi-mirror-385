#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/8 20:03:21

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
from ..trans.op import mat_angle_axis
from laok.base.alg import arr_split_n
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ =[
          'CldScaleRand', 'CldTranslateRand', 'CldJitter', 'CldDropout',
          'CldRotateRand', 'CldRotatePerturbationRand',
          'CldRepeat'
          ]

class CldScaleRand:
    def __init__(self, lo=0.8, hi=1.25):
        self.lo, self.hi = lo, hi

    def __call__(self, points):
        scaler = np.random.uniform(self.lo, self.hi)
        points[:] *= scaler
        return points

class CldTranslateRand:
    def __init__(self, shift_range=0.1):
        self.shift_range = shift_range

    def __call__(self, points):
        translation = np.random.uniform(-self.shift_range, self.shift_range)
        points[:] += translation
        return points

class CldRotateRand:
    def __init__(self, axis=np.array([0.0, 1.0, 0.0])):
        self.axis = axis

    def __call__(self, points):
        rotation_angle = np.random.uniform() * 2 * np.pi
        rm = mat_angle_axis(rotation_angle, self.axis)

        normals = points.shape[1] > 3
        if not normals:
            return np.matmul(points, np.transpose(rm))
        else:
            pc_xyz = points[:, 0:3]
            pc_normals = points[:, 3:]
            points[:, 0:3] = np.matmul(pc_xyz, np.transpose(rm))
            points[:, 3:] = np.matmul(pc_normals, np.transpose(rm))
            return points

class CldRotatePerturbationRand:
    def __init__(self, angle_sigma=0.06, angle_clip=0.18):
        self.angle_sigma, self.angle_clip = angle_sigma, angle_clip

    def _get_angles(self):
        angles = np.clip(
            self.angle_sigma * np.random.randn(3), -self.angle_clip, self.angle_clip
        )
        return angles

    def __call__(self, points):
        angles = self._get_angles()
        Rx = mat_angle_axis(angles[0], np.array([1.0, 0.0, 0.0]))
        Ry = mat_angle_axis(angles[1], np.array([0.0, 1.0, 0.0]))
        Rz = mat_angle_axis(angles[2], np.array([0.0, 0.0, 1.0]))

        rm = np.matmul(np.matmul(Rz, Ry), Rx)

        normals = points.shape[1] > 3
        if not normals:
            return np.matmul(points, np.transpose(rm))
        else:
            pc_xyz = points[:, 0:3]
            pc_normals = points[:, 3:]
            points[:, 0:3] = np.matmul(pc_xyz, np.transpose(rm))
            points[:, 3:] = np.matmul(pc_normals, np.transpose(rm))
            return points

class CldJitter(object):
    def __init__(self, std=0.01, clip=0.05):
        self.std, self.clip = std, clip

    def __call__(self, points):
        N = points.shape[0]
        jittered_data = np.clip(self.std * np.random.randn(N, 3), -1*self.clip, self.clip)
        points[:, 0:3] += jittered_data
        return points

class CldDropout(object):
    def __init__(self, max_dropout_ratio=0.875):
        assert max_dropout_ratio >= 0 and max_dropout_ratio < 1
        self.max_dropout_ratio = max_dropout_ratio

    def __call__(self, points):
        dropout_ratio = np.random.random() * self.max_dropout_ratio  # 0~0.875
        drop_idx = np.where(np.random.random((points.shape[0])) <= dropout_ratio)[0]
        if len(drop_idx) > 0:
            points[drop_idx] = points[0]  # set to the first point
        return points  # torch.from_numpy(pc).float()

class CldRepeat:
    def __init__(self, count=4):
        self.count = count

    def __call__(self, points):
        sub_points = arr_split_n(points, self.count)

        points1, points2 = arr_split_n(points, self.count)
        x1 = np.ptp(points1, axis=0)[0]
        x2 = np.ptp(points2, axis=0)[0]
        points1[:] -= np.array([x1/2+0.01, 0, 0])
        points2[:] += np.array([x2/2+0.01, 0, 0])
        return np.concatenate(sub_points, axis=0)