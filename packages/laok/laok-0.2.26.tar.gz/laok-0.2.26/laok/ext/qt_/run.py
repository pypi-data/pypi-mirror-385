#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/14 10:13:56

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from PyQt5.QtWidgets import QApplication, QWidget
import sys, inspect
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['run_widget']

def run_widget(widget = None, init_func = None, clear_func = None, *args, **kwargs):

    try:
        app = QApplication(sys.argv)

        if init_func:
            init_func(app)

        win = widget
        if inspect.isclass(widget) or inspect.isfunction(widget):
            win = widget(*args, **kwargs)

        if isinstance(win, QWidget):
            win.show()

        ret = app.exec_()

        if clear_func:
            clear_func(app)

        sys.exit(ret)

    except Exception as e:
        import traceback
        traceback.print_exc()
