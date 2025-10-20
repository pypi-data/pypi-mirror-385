#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 13:02:51

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from collections import defaultdict
from io import StringIO
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['g_factory']

class ObjectFactory:
    def __init__(self):
        self._creator_list = defaultdict(list)
        self._name_list = defaultdict(list)

    def get_creator(self, _name, category=None, *args, **kws):
        for creator in self.get_creator_list(category):
            _ctor = creator(_name, *args, **kws)
            if _ctor:
                return _ctor

    def get_instance(self, _name, category=None, _args=None, _kws=None, *args, **kws):
        if _args is None: _args = ()
        if _kws is None: _kws = {}
        if args is None: args = ()
        ctor = self.get_creator(category, _name, *_args, **_kws)
        if ctor:
            return ctor(*args, **kws)

    def _add_name(self, _list, name):
        if name:
            _list.append(name)

    def add_name(self, category, *names):
        _list = self._name_list[category]
        for name in names:
            if isinstance(name, (tuple, list)):
                for _name in name:
                    self._add_name(_list, _name)
            elif name:
                self._add_name(_list, name)

    def add_creator(self, category, creator):
        self._creator_list[category].append(creator)

    def register(self, category, *names):
        self.add_name(category, *names)
        def inner(creator):
            self.add_creator(category, creator)
            def inner2(name):
                return creator(name)
            return inner2
        return inner

    def get_name_list(self, category=None):
        if category:
            return self._name_list[category]
        else:
            _name_list = []
            for v in self._name_list.values():
                _name_list.extend(v)
            return _name_list

    def get_creator_list(self, category=None):
        if category:
            return self._creator_list[category]
        else:
            _ctor_list = []
            for v in self._creator_list.values():
                 _ctor_list.extend(v)
            return _ctor_list

    def __str__(self):
        s = StringIO()
        width = 80
        for cat, namelist in self._name_list.items():
            s.write(cat + f" ({len(namelist)})\n")
            _w, _i, _len = 0, 0, len(namelist)
            for i in range(0, _len):
                _w += len(namelist[i])
                if _w > width:
                    s.write("\t" + ", ".join(namelist[_i:i-1]) + "\n")
                    _i, _w = i-1, 0
            s.write("\t" + ", ".join(namelist[_i:_len]) + "\n")
        return s.getvalue()

# 全局注册工厂
g_factory = ObjectFactory()