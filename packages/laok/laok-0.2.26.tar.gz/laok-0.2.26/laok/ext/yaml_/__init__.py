#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 19:56:46

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import yaml
from collections import OrderedDict
from laok.base.alg import Dict
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['save_yaml_file', 'load_yaml_file']

def save_yaml_file(filename, obj, indent=2, **kws):
    with open(filename, mode='w', encoding='utf8') as f:
        if isinstance(obj, (OrderedDict, Dict) ):
            _dict_dump(obj, f, indent=indent, **kws)
        else:
            yaml.safe_dump(data=obj, stream=f, indent=indent,**kws)
    return True

def load_yaml_file(filename, **kws):
    with open(filename, encoding='utf8') as f:
        return yaml.safe_load(f, **kws)

def _dict_dump(data, stream=None, **kwds):
    class DictDumper(yaml.Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())

    DictDumper.add_representer(OrderedDict, _dict_representer)
    DictDumper.add_representer(Dict, _dict_representer)
    return yaml.dump(data, stream, DictDumper, **kwds)
