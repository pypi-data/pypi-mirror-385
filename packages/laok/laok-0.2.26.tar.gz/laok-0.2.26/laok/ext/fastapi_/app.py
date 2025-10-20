#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/15 09:55:29

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from fastapi import FastAPI
app = FastAPI()
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['app', 'run']


def run(host: str = "127.0.0.1",  port: int = 8000, **kws):
   import uvicorn
   uvicorn.run(app=app, host=host, port=port, **kws)
