#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2021/3/17 21:11:08

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import time, sys
from functools import wraps
from collections import OrderedDict

from contextlib import contextmanager
#===============================================================================
# 
#===============================================================================
__all__ = ['time_sleep', 'time_deco', 'time_ctx', 'Timer', 'TimerLabel']

time_sleep = time.sleep

def time_deco(stream = None):
    ''' 装饰器,记录时间 '''
    def _w1(func):
        @wraps(func)
        def _w2(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            stop = time.time()
            _stream = stream or sys.stdout
            _stream.write(f"[{ func.__name__ }] use time [{ 1000*(stop-start) }(ms)]\n")
            return res
        return _w2
    return _w1


@contextmanager
def time_ctx(msg=None, stream=None):
    '''上下文计时器'''
    t1 = time.time()
    yield
    t2 = time.time()
    eps = (t2-t1)*1000

    _stream = stream or sys.stdout
    if msg is not None:
        _stream.write(f'{msg} ')
    _stream.write(f'time:{eps}(ms)\n')


class Timer:
    def __init__(self):
        self.restart()

    def restart(self):
        self._t1 = time.time()

    def elapse(self): #单位 (s)
        return time.time() - self._t1


class TimerLabel:
    def __init__(self):
        self._t1 = OrderedDict()
        self._t2 = OrderedDict()
        self._enabled = True
        self._total_count = None
        self._cur_count = 0

    def setEnabled(self, val):
        self._enabled = val

    def setReportCount(self, cnt):
        self._total_count = cnt
        self._cur_count = 0

    def start(self, name):
        if self._enabled:
            self._t1[name] = time.time()

    def end(self, name):
        if self._enabled:
            self._t2[name] = time.time()

    def report(self, stream = None):
        if not self._enabled:
            return 
        
        if self._total_count is not None:
            if self._cur_count >= self._total_count:
                return
            self._cur_count += 1

        _stream = stream or sys.stdout
        
        curt = time.time()
        _stream.write("\n***** time summary *****\n")
        for name,t1 in self._t1.items():
            t2 = self._t2.get(name, curt)
            _stream.write(f'"{name}" time use: {t2-t1}(s)\n')

if __name__ == "__main__":
    times = TimerLabel()
    times.setReportCount(2)

    for i in range(5):
        times.start('it1')
        time.sleep(1)
        times.start('it2')
        time.sleep(3)
        times.report()