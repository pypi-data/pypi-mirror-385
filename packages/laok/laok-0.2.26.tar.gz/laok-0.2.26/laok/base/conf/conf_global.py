#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 22:39:34
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
from ..fs import path_replace_basename
from ..alg.addict import Dict
#===============================================================================
r'''全局配置
'''
#===============================================================================
__all__ = ['g_conf', 'conf_update', 'conf_merge', 'conf_merge_file']
g_conf = Dict()

def conf_update(**kws):
    g_conf.update(**kws)

def conf_merge(data):
    g_conf.update(data)

def conf_merge_file(fname):
    if fname.endswith('.json'):
        import json
        with open(fname, encoding='utf8') as f:
            _data = json.load(f)
            conf_merge(_data)
    elif fname.endswith('.yaml'):
        import yaml
        with open(fname, encoding='utf8') as f:
            _data = yaml.safe_load(f)
            conf_merge(_data)

#默认配置文件
_conf_file = path_replace_basename(__file__, 'conf.yaml')
conf_merge_file(_conf_file)

#读取环境变量配置
_env_path = os.environ.get('LAOK_CONF_PATH')
if _env_path and os.path.exists(_env_path):
    conf_merge_file(_env_path)

