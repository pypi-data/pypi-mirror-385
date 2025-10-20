#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/14 16:01:34

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''

# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['arr_split_n']

def arr_split_n(arr, n):
    ''' 把数组分割成n段,并尽可能长度接近; 也可以用 np.array_split(arr, n)
    '''
    k, m = divmod(len(arr), n)
    return [arr[i*k + min(i, m):(i+1)*k + min(i+1, m)]
                for i in range(n)]


