#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/5/4 20:27:02
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
from ultralytics import YOLO
import laok
from laok.ext.cv2_.io import fix_cv_read
from laok.ext.yaml_ import save_yaml_file
from laok import log_info

from .export import export_onnx
#===============================================================================
r'''支持 yolo训练的脚本
需要 文件夹 root_dir下:
                ---- xxx.pt
                ---- xxx.names
                ---- Image/
imgsz = (height, width)
'''
#===============================================================================
__all__ = ['train_det', 'train_cls', 'train_seg', 'train_obb', 'train_pose']


def _train(root_dir, train_path='Image', val_path='Image', test_path=None, model_file=None, **kws):
    log_info(f'root_dir= {root_dir}')
    fix_cv_read()

    with laok.workdir_scope(root_dir):
        if model_file is None:
            model_file = laok.path_search_cur_ext('.', ".pt")

        # ### 删除.cache
        # for fname in laok.path_search_under_ext(train_path, '.cache'):
        #     log_info(f'delete file:{fname}')
        #     laok.file_delete(fname)

        ### 生成 yaml
        ds = laok.Dict()
        ds.path = os.getcwd()
        ds.train = train_path
        ds.val = val_path
        ds.test = test_path
        if 'kpt_shape' in kws:
            ds.kpt_shape = kws.pop('kpt_shape')
        if 'flip_idx' in kws:
            ds.flip_idx = kws.pop('flip_idx')
        names_file = laok.path_search_cur_ext('.', ".names")
        ds.names = list(line.split(":")[0] for line in laok.file_read_lines(names_file))
        data_file = laok.path_replace_ext(model_file, ".yaml")
        save_yaml_file(data_file, ds, indent=4, encoding='utf8')

        ### 训练
        model = YOLO(model_file)
        kws['data'] = data_file
        kws.setdefault('save_txt', True)
        kws.setdefault('save_conf', True)
        kws.setdefault('save_crop', True)
        kws.setdefault('amp', False)
        kws.setdefault('degrees', 3)
        if laok.is_windows():
            kws.setdefault('workers', 0)
        model.train(**kws)

        # 导出onnx
        dst_file = kws.pop('dst_file', None)
        best_model = laok.path_search_under_file(str(model.trainer.wdir), 'best.pt')
        export_onnx(best_model, imgsz=kws['imgsz'], dst_file=dst_file)


def _train_cls(root_dir, image_path='Image', model_file=None, **kws):
    log_info(f'root_dir= {root_dir}')
    fix_cv_read()
    with laok.workdir_scope(root_dir):
        if model_file is None:
            model_file = laok.path_search_cur_ext('.', ".pt")

        from torchvision.datasets.folder import find_classes
        data_dir = image_path
        if os.path.exists( os.path.join(image_path, 'train') ):
            data_dir = os.path.join(image_path, 'train')
        classes, class_to_idx = find_classes(data_dir)
        laok.file_write_lines('cls.names', classes, encoding='gbk')

        ### 训练
        model = YOLO(model_file)
        kws['data'] = image_path
        kws.setdefault('save_txt', True)
        kws.setdefault('save_conf', True)
        kws.setdefault('save_crop', True)
        kws.setdefault('amp', False)
        kws.setdefault('degrees', 3)
        if laok.is_windows():
            kws.setdefault('workers', 0)
        model.train(**kws)

        # 导出onnx
        dst_file = kws.pop('dst_file', None)
        best_model = laok.path_search_under_file(str(model.trainer.wdir), 'best.pt')
        export_onnx(best_model, imgsz=kws['imgsz'], dst_file=dst_file)



def train_det(root_dir, imgsz=(640, 640), epochs=100, batch=16, **kws):
    _train(root_dir=root_dir, task='detect', imgsz=imgsz, epochs=epochs, batch=batch, **kws)

def train_seg(root_dir, imgsz=(640, 640), epochs=100, batch=16, **kws):
    _train(root_dir=root_dir, task='segment', imgsz=imgsz, epochs=epochs, batch=batch, **kws)


def train_cls(root_dir, imgsz=(640, 640), epochs=100, batch=16, **kws):
    _train_cls(root_dir=root_dir, task='classify', imgsz=imgsz, epochs=epochs, batch=batch, **kws)


def train_obb(root_dir, imgsz=(640, 640), epochs=100, batch=16, **kws):
    _train(root_dir=root_dir, task='obb', imgsz=imgsz, epochs=epochs, batch=batch, **kws)


def train_pose(root_dir, kpt_shape, imgsz=(640, 640), epochs=100, batch=16, **kws):
    _train(root_dir=root_dir, kpt_shape=kpt_shape, task='pose', imgsz=imgsz, epochs=epochs, batch=batch, **kws)

