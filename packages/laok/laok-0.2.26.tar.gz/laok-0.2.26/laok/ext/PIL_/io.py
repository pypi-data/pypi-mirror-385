#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/14 20:16:56

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from PIL import Image
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['read_image', ]


def read_image(file):
    return Image.open(file)


