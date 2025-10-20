#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 17:21:57
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from collections import OrderedDict
from ..str import dict_to_str
from ..fs import file_read_lines, file_write_lines
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['NameIndexFile', 'cls_to_name']

# 根据配置文件获取索引
class NameIndexFile:
    def __init__(self, cls_file = None):
        self.cls_data_ = OrderedDict()
        if cls_file:
            self.setClsFile(cls_file)

    def setClsFile(self, cls_file):
        for i,line in enumerate(file_read_lines(cls_file)):
            self.cls_data_[i] = line
        return self

    def getName(self, idx):
        _idx = int(idx)
        return self.cls_data_.get(_idx, f'Unknow[{idx}]')

    def getIndex(self, name):
        if name:
            for _idx, _name in self.cls_data_.items():
                if name in _name:
                    return _idx
        return -1

    def getData(self):
        return self.cls_data_

    def __str__(self):
        return dict_to_str(self.cls_data_, start=20, stop=20)

def cls_to_name(index, filename):
    nameIdx = NameIndexFile(filename)
    return nameIdx.getName(index)
