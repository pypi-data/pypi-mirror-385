#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 10:30:01

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import time
from datetime import datetime
from .fpath import path_join, path_make_parent
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['PathGenSeq', 'PathGenTimed']

class _PathGenBase:
    def __init__(self, parent="", ext="", stem_pre="", stem_suf="", create_dir=False):
        self.setParent(parent)
        self.setExt(ext)
        self.setStemPre(stem_pre)
        self.setStemSuf(stem_suf)
        self.setCreateDir(create_dir)

    def setExt(self, ext):
        if ext:
            self._ext = ext if ext.startswith(".") else '.' + ext

    def setStemPre(self, stem_pre):
        self._stem_pre = stem_pre

    def setStemSuf(self, stem_suf):
        self._stem_suf = stem_suf

    def setParent(self, parent):
        self._parent = parent

    def setCreateDir(self, create_dir):
        self._create_dir = create_dir

    def _get_stem(self): # 需要覆盖该函数,实现序列化名字
        return ""

    def __next__(self):
        return self.next_path()

    def __iter__(self):
        return self

    def next_path(self):
        if self._create_dir:
            make_parent = True
            self._create_dir = False
        else:
            make_parent = False
        pth = path_join(self._parent, self._stem_pre + self._get_stem() + self._stem_suf + self._ext,
                        make_parent=make_parent)
        return pth

    def __call__(self):
        return self.next_path()


class PathGenSeq(_PathGenBase):
    def __init__(self, parent="", ext="", start=0, width=8, stem_pre="", stem_suf="", create_dir=False):
        super().__init__(parent=parent, ext=ext, stem_pre=stem_pre, stem_suf=stem_suf, create_dir=create_dir)
        self._start = start
        self._width = width

    def _get_stem(self):
        fmt = "{:0" + str(self._width) + "}"
        fname = fmt.format(self._start)
        self._start += 1
        return fname

class PathGenTimed(_PathGenBase):
    def __init__(self, parent="", ext="", time_fmt="%Y%layer%d_%H%M%S", stem_pre="", stem_suf="", create_dir=False):
        super().__init__(parent=parent, ext=ext, stem_pre=stem_pre, stem_suf=stem_suf, create_dir=create_dir)
        self._last_tick = 0
        self._last_inc = 0
        self._time_fmt = time_fmt

    def _get_stem(self):
        cur_time = int(time.time())
        dt = datetime.fromtimestamp(cur_time)
        if self._last_tick != cur_time:
            self._last_inc = 0
            self._last_tick = cur_time
            return dt.strftime(self._time_fmt)
        else:
            self._last_inc += 1
            self._last_tick = cur_time
            return dt.strftime(self._time_fmt) + "-" +str(self._last_inc)
