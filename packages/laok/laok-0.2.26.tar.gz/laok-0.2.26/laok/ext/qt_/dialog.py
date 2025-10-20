#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/14 10:28:02

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from PyQt5.QtWidgets import QFileDialog
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['dialog_file']

def dialog_file(filter='(*.*)', directory=None, **kws):
    kws.setdefault('caption', 'open file')
    return QFileDialog.getOpenFileName(directory=directory, filter=filter, **kws)
