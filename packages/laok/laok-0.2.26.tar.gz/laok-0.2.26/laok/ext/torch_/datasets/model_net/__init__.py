#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/9/18 11:31:01

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from .._creator import ctor
# ===============================================================================
r'''
'''
# ===============================================================================

name_list = ['Modelnet',
             'ModelnetIneratia',
             'ModelnetNormals',
             'ModelnetNormalsDiff']

@ctor.register(*name_list)
def _get(_name, **kws):
    DS = None

    if _name == 'Modelnet':
        from .model_net import Modelnet as DS
    elif _name == 'ModelnetIneratia':
        from .model_net_ineratia import ModelnetIneratia as DS
    elif _name == 'ModelnetNormals':
        from .model_net_normals import ModelnetNormals as DS
    elif _name == 'ModelnetNormalsDiff':
        from .model_net_normals import ModelnetDiffNormals as DS

    if DS:
        return DS(**kws)
