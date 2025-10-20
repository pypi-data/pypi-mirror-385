#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/20 18:31:49

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import os, shutil
import laok
from ..fs import path_parent
from ..proc import workdir_scope
# ===============================================================================
r'''
'''
# ===============================================================================

def pypi_upload(lib_dir=None, rm_temp=True, upload = True):
    if not lib_dir:
        lib_dir = path_parent(__file__, 4)

    print(f'lib_dir = {lib_dir}')

    # 切换到 lib_dir
    with workdir_scope(lib_dir):

        # 编译工具包
        os.system('python setup.py sdist')

        # 上传到pypi
        if upload:
            os.system('twine upload dist/*.gz')

        if rm_temp:  #删除临时文件
            for rmdir in ['build', 'dist', 'laok.egg-info']:
                shutil.rmtree(rmdir, ignore_errors=True)