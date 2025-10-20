#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2020/7/21 10:33:17

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os, sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QDialog
from PyQt5.uic import loadUi, compileUi
from laok.base import log_info
#===============================================================================
#
#===============================================================================

__all__ = ['UiMainWindowDy', 'UiDyWidget', 'UiDyDialog', 'widget_from_ui', 'compile_ui_file']

def _init_ui_file(obj):
    if hasattr(obj, 'ui_file'):
        ui_file = getattr(obj, 'ui_file')
    else:
        module_file = sys.modules[obj.__module__].__file__
        ui_file = os.path.splitext(module_file)[0] + ".ui"
    if not os.path.exists(ui_file):
        raise ValueError(f"you need config 'ui_file' in your class of[{obj.__class__}]")
    else:
        log_info(f' load ui file= {ui_file}')
    loadUi(ui_file, obj)  # 初始化Ui

def widget_from_ui(ui_file):
    log_info(f' load ui file= {ui_file}')
    return loadUi(ui_file)

class UiMainWindowDy(QMainWindow):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        QMainWindow.__init__(obj)
        _init_ui_file(obj)
        return obj

    def __init__(self):
        pass

class UiDyWidget(QWidget):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        QWidget.__init__(obj)
        _init_ui_file(obj)
        return obj

    def __init__(self):
        pass

class UiDyDialog(QDialog):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        QDialog.__init__(obj)
        _init_ui_file(obj)
        return obj

    def __init__(self):
        pass

def compile_ui_file(ui_file, save_file=None):
    '''
        保存 X_ui.py 文件
    '''
    if save_file is None:
        save_file = os.path.splitext(ui_file)[0] + '_ui.py'
    with open(save_file, 'w', encoding='utf8') as f:
        compileUi(uifile=ui_file, pyfile=f)
