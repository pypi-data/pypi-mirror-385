#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 15:45:43

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from lxml import objectify
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['get_maker']

def get_maker(**kws):
    kws.setdefault('annotate', False)
    return objectify.ElementMaker(**kws)