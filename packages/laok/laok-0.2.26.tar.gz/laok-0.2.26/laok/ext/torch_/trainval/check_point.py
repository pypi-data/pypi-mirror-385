#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/16 14:54:01

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
import torch
import laok
from laok.ext.torch_.io import load_model_params
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['CheckPointBest', 'select_best_model_file', 'load_best_model']

####################    支持搜索加载最优的参数模型
class CheckPointBest:
    def __init__(self, model, save_dir, tag=None, load_path=True, keep_best=False, show_info=True):
        self._save_dir = save_dir if save_dir else "out/" + laok.datetime_fmt()
        if save_dir is None:
            self._save_dir = "out/" + laok.datetime_fmt()
            self._tag = 'model' if tag is None else tag
        else:
            self._save_dir = save_dir
            self._tag = laok.path_stem(save_dir) if tag is None else tag

        self._keep_best = keep_best
        self.show_info = show_info
        if self.show_info:
            laok.log_info(f'===== {self.__class__.__name__}')
            laok.log_info(f"tag: {self._tag}, keep_best:{self._keep_best}, path:{self._save_dir}")

        self._name_value = {}
        self._value = None
        self._is_keep_best = False
        self.set_model(model)
        if load_path:
            self.load_from_path()

    def set_model(self, model):
        self._model = model

    def update(self, value):
        '''the model needs to be saved according to the value
        '''
        # check if need save model
        if self._value is None or self._value < value:
            self._value = value  # update the best value
            save_file = laok.path_join(self._save_dir, f'{self._tag}-{self._value:.4f}.pth', make_parent=True)
            torch.save(self._model.state_dict(), save_file)
            if self.show_info:
                laok.log_info(f'save checkpoint: {save_file}')

        if self._value == value:
            if self.show_info:
                laok.log_info(f"current {self._tag} value is {value:.4f}, it's the best.!!!")
        else:
            if self.show_info:
                laok.log_info(f'current {self._tag} value is {value:.4f}, while the best value is {self._value:.4f}')
            if self._keep_best:
                self._is_keep_best = True
                if self.show_info:
                    laok.log_info(f"keep best")
                self.load_from_path()
                self._is_keep_best = False

    def load_from_path(self):
        max_value_file, max_value = _select_best_mode_file(self._save_dir)
        if max_value_file:
            self.load_from_file(max_value_file, max_value)

    def load_from_file(self, model_file, value=None):
        if not os.path.exists(model_file):
            return
        if self.show_info:
            laok.log_info(f'load checkpoint file: {model_file}')
        load_model_params(self._model, model_file)
        _value = _score_from_path(model_file)
        self._value = _value if value is None else value

def select_best_model_file(dir):
    filename, val = _select_best_mode_file(dir)
    return filename

def load_best_model(model, dir, show_info=True):
    model_file = select_best_model_file(dir)
    if show_info:
        laok.log_info(f'load checkpoint file: {model_file}')
    load_model_params(model, model_file)
    return model

def _select_best_mode_file(dir):
    max_value = None
    max_value_file = None

    for fname in laok.files_under(dir, '.pth'):
        _value = _score_from_path(fname)
        if max_value is None or max_value < _value:
            max_value = _value
            max_value_file = fname

    return max_value_file, max_value

def _score_from_path(filename):
    stem = laok.path_stem(filename)
    value = stem.split('-')[-1]
    return laok.float_value(value, 0.0)
