#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2021/3/17 10:36:20

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import random
from ..fs import file_read_lines, path_replace_basename
#===============================================================================
#
#===============================================================================
__all__ = ['color_rand', 'color_rand_seed']

_color_map = {}
_color_set = set()
_rand = random.Random()

def _add_color(color):
    _color_map[len(_color_map)] = color
    _color_set.add(color)

def _init_color_list():
    if not _color_map:
        fname = path_replace_basename(__file__, 'color_list.txt')
        for line in file_read_lines(fname):
            ds = line.split(',')
            r,g,b = int(ds[0]), int(ds[1]), int(ds[2])
            _add_color((r,g,b))

def _gen_color():
    for i in range(3):
        r = _rand.randint(0,255)
        g = _rand.randint(0,255)
        b = _rand.randint(0,255)
        c = (r,g,b)
        if c in _color_set:
            continue
        return c

def color_rand(idx = None):
    '''
    :param idx:  color index, when None, rand a color
    :return:
    '''
    if idx is None:
        return _gen_color()
    else:
        idx = int(idx)
        _init_color_list()
        if idx in _color_map:
            return _color_map[idx]
        c = _gen_color()
        _add_color(c)
        return c

def color_rand_seed(seed):
    _rand.seed(seed)

if __name__ == "__main__":
    res = color_rand()
    print(res)
    res = color_rand()
    print(res)
    res = color_rand(10)
    print(res)
