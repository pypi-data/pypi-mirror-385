#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/13 12:07:09

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''

# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['kws_merge']


def kws_merge(kws, **kwargs):
    if kws is None:
        kws = {}
    kws.update(kwargs)
    return kws
