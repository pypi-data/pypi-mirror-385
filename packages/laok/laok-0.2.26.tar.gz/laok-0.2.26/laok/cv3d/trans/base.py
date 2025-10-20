#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/13 21:23:49

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
from .op import mat_angle_axis
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['CldScale', 'CldTranslate', 'CldNormal', 'CldTransform', 'CldRotateX', 'CldRotateY', 'CldRotateZ',
           'CldRotateXYZ']

class CldScale:
    def __init__(self, scale_x = 1.0, scale_y = 1.0, scale_z = 1.0):
        self.x = scale_x
        self.y = scale_y
        self.z = scale_z

    def __call__(self, points):
        points[:, 0] *= self.x
        points[:, 1] *= self.y
        points[:, 2] *= self.z
        return points

class CldTranslate(object):
    def __init__(self, shift_x = 0, shift_y = 0, shift_z = 0):
        self.x = shift_x
        self.y = shift_y
        self.z = shift_z

    def __call__(self, points):
        points[:, 0] += self.x
        points[:, 1] += self.y
        points[:, 2] += self.z
        return points

class CldTransform:
    def __init__(self, mat):
        self.mat = mat

    def __call__(self, points):
        has_normal = points.shape[1] > 3
        if not has_normal:
            return np.matmul(points, np.transpose(self.mat))
        else:
            pc_xyz = points[:, 0:3]
            pc_normals = points[:, 3:]
            points[:, 0:3] = np.matmul(pc_xyz, np.transpose(self.mat))
            points[:, 3:] = np.matmul(pc_normals, np.transpose(self.mat))
            return points

class CldRotateX:
    def __init__(self, angle = 90):
        self.angle = angle

    def __call__(self, points):
        axis = np.array([1.0, 0.0, 0.0])
        mat = mat_angle_axis(self.angle, axis)
        return CldTransform(mat)(points)

class CldRotateY:
    def __init__(self, angle = 90):
        self.angle = angle

    def __call__(self, points):
        axis = np.array([0.0, 1.0, 0.0])
        mat = mat_angle_axis(self.angle, axis)
        return CldTransform(mat)(points)

class CldRotateZ:
    def __init__(self, angle = 90):
        self.angle = angle

    def __call__(self, points):
        axis = np.array([0.0, 0.0, 1.0])
        mat = mat_angle_axis(self.angle, axis)
        return CldTransform(mat)(points)


class CldRotateXYZ:
    def __init__(self, angle_x=90, angle_y=0, angel_z=0):
        self.angle_x = angle_x
        self.angle_y = angle_y
        self.angle_z = angel_z

    def __call__(self, points):
        Rx = mat_angle_axis(self.angle_x, np.array([1.0, 0.0, 0.0]))
        Ry = mat_angle_axis(self.angle_y, np.array([0.0, 1.0, 0.0]))
        Rz = mat_angle_axis(self.angle_z, np.array([0.0, 0.0, 1.0]))
        mat = np.matmul(np.matmul(Rz, Ry), Rx)
        return CldTransform(mat)(points)

class CldNormal:
    def __call__(self, points):
        centroid = np.mean(points, axis=0)
        points -= centroid
        m = np.max(np.sqrt(np.sum(points ** 2, axis=1)))
        points /= m
        return points