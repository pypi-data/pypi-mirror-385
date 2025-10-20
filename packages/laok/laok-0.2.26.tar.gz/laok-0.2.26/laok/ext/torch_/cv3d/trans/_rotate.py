#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/21 17:01:47
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import math
import numpy as np
from scipy.spatial.transform import Rotation
#===============================================================================
r'''
'''
#===============================================================================
__all__ = [
            'CldRotate',
            'CldRotatePerturbation',
            'rotate_matrix_from_angle_axis',
            'is_rotation_matrix',
            'rotation_matrix_to_euler',
            'euler_to_rotate_matrix',
            'euler_to_rotate_vec',
           ]



class CldRotate(object):
    def __init__(self, axis=np.array([0.0, 1.0, 0.0])):
        self.axis = axis

    def __call__(self, points):
        rotation_angle = np.random.uniform() * 2 * np.pi
        rotation_matrix = rotate_matrix_from_angle_axis(rotation_angle, self.axis)

        normals = points.shape[1] > 3
        if not normals:
            return np.matmul(points, rotation_matrix.transpose())
        else:
            pc_xyz = points[:, 0:3]
            pc_normals = points[:, 3:]
            points[:, 0:3] = np.matmul(pc_xyz, rotation_matrix.transpose())
            points[:, 3:] = np.matmul(pc_normals, rotation_matrix.transpose())

            return points


class CldRotatePerturbation(object):
    def __init__(self, angle_sigma=0.06, angle_clip=0.18):
        self.angle_sigma, self.angle_clip = angle_sigma, angle_clip

    def _get_angles(self):
        angles = np.clip(
            self.angle_sigma * np.random.randn(3), -self.angle_clip, self.angle_clip
        )

        return angles

    def __call__(self, points):
        angles = self._get_angles()
        Rx = rotate_matrix_from_angle_axis(angles[0], np.array([1.0, 0.0, 0.0]))
        Ry = rotate_matrix_from_angle_axis(angles[1], np.array([0.0, 1.0, 0.0]))
        Rz = rotate_matrix_from_angle_axis(angles[2], np.array([0.0, 0.0, 1.0]))

        rotation_matrix = np.matmul(np.matmul(Rz, Ry), Rx)

        normals = points.shape[1] > 3
        if not normals:
            return np.matmul(points, rotation_matrix.transpose())
        else:
            pc_xyz = points[:, 0:3]
            pc_normals = points[:, 3:]
            points[:, 0:3] = np.matmul(pc_xyz, rotation_matrix.transpose())
            points[:, 3:] = np.matmul(pc_normals, rotation_matrix.transpose())

            return points

def rotate_matrix_from_angle_axis(angle, axis):
    # type: (float, np.ndarray) -> float
    r"""Returns a 3x3 rotation matrix that performs a rotation around axis by angle

    Parameters
    ----------
    angle : float
        Angle to rotate by
    axis: np.ndarray
        Axis to rotate about

    Returns
    -------
    np.ndarray
        3x3 rotation matrix
    """
    u = axis / np.linalg.norm(axis)
    cosval, sinval = np.cos(angle), np.sin(angle)

    # yapf: disable
    cross_prod_mat = np.array([[0.0, -u[2], u[1]],
                                [u[2], 0.0, -u[0]],
                                [-u[1], u[0], 0.0]])

    R = cosval * np.eye(3) \
        + sinval * cross_prod_mat \
        + (1.0 - cosval) * np.outer(u, u)
    return R


def is_rotation_matrix(R) :
    Rt = np.transpose(R)
    shouldBeIdentity = np.dot(Rt, R)
    I = np.identity(3, dtype = R.dtype)
    n = np.linalg.norm(I - shouldBeIdentity)
    return n < 1e-6


def rotation_matrix_to_euler(R, err=1e-6) :
    sy = math.sqrt(R[0,0] * R[0,0] +  R[1,0] * R[1,0])
    singular = sy < err
    if  not singular :
        x = math.atan2(R[2,1] , R[2,2])
        y = math.atan2(-R[2,0], sy)
        z = math.atan2(R[1,0], R[0,0])
    else :
        x = math.atan2(-R[1,2], R[1,1])
        y = math.atan2(-R[2,0], sy)
        z = 0
    return np.array([x, y, z])

def euler_to_rotate_matrix(yaw, pitch, roll):
    Rz_yaw = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]])
    Ry_pitch = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]])
    Rx_roll = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]])
    # R = RzRyRx
    rotMat = np.dot(Rz_yaw, np.dot(Ry_pitch, Rx_roll))
    return rotMat

def euler_to_rotate_vec(yaw, pitch, roll):
    # compute the rotation matrix
    Rmat = euler_to_rotate_matrix(yaw, pitch, roll)

    theta = math.acos(((Rmat[0, 0] + Rmat[1, 1] + Rmat[2, 2]) - 1) / 2)
    sin_theta = math.sin(theta)
    if sin_theta == 0:
        rx, ry, rz = 0.0, 0.0, 0.0
    else:
        multi = 1 / (2 * math.sin(theta))
        rx = multi * (Rmat[2, 1] - Rmat[1, 2]) * theta
        ry = multi * (Rmat[0, 2] - Rmat[2, 0]) * theta
        rz = multi * (Rmat[1, 0] - Rmat[0, 1]) * theta
    return rx, ry, rz

