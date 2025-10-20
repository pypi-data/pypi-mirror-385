#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/19 16:51:55

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from datetime import datetime
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['fmt_datetime', ]

def fmt_datetime(fmt='%Y%m%d_%H%M%S', dt = None):
    if dt is None:
        dt = datetime.now()
    return dt.strftime(fmt)

if __name__ == '__main__':
    dt = fmt_datetime()
    print(dt)
