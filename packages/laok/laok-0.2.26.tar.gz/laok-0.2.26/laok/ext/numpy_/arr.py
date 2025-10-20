#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/14 17:03:09

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import numpy as np

# ===============================================================================
r'''
'''
# ===============================================================================

import numpy as np

# 创建一个示例多维数组（3D 数组）
arr = np.array(
    [
        [0, 2, 3],
        [4, 5, 6],
        [7, 8, 9],
        [10, 11, 12],
        [13, 14, 15],
        [16, 17, 18]
    ])

# 计算第 0 维（行方向）的极差
range_0 = np.ptp(arr, axis=0)
print("第 0 维的极差：\n", range_0)

# 计算第 1 维（列方向）的极差
range_1 = np.ptp(arr, axis=1)
print("第 1 维的极差：\n", range_1)
