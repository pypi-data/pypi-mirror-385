#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 22:43:12
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from flask import Flask, request
#===============================================================================
r'''web服务
'''
#===============================================================================
__all__ = ['app', 'run', 'req_param', 'req_files']

app = Flask(__name__)

run = app.run

def req_param(name=None):
    if request.method == 'POST':
        data = request.form
    else:
        data = request.args

    if name is None:
        return data
    return data.get(name)

def req_files():
    return
