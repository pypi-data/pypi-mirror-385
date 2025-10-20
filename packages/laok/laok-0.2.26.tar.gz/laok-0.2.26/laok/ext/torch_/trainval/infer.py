#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 21:25:44

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import torch
import laok
from tqdm import tqdm
from ..op.device import get_device
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['infer_cls_one', 'infer_cls_batch', 'infer_cls_dataloader']

def infer_cls_one(model, data):
    batch_data = data.unsqueeze(0)
    pred_choice = infer_cls_batch(model, batch_data)
    return pred_choice[0]

def infer_cls_batch(model, data):
    model.eval()
    _device = get_device(model)
    with torch.no_grad():
        pred = model(data.to(_device))
        pred_choice = pred.max(1)[1]
        return [v.item() for v in pred_choice]

def infer_cls_dataloader(model, loader):
    mean_correct = []
    # class_acc = None
    laok.log_info('val data_loader')

    pbar = tqdm(enumerate(loader), total=len(loader), smoothing=0.9)
    for j, (data, target) in pbar:
        d_size_str = laok.size_to_str(data.size())
        t_size_str = laok.size_to_str(target.size())
        pbar.set_description(f"validate data:{d_size_str} target:{t_size_str}")
        mean_val, pred_choice = infer_cls_batch(model, data, target)
        mean_correct.append(mean_val)
        # print(f"mean_val:{mean_val}")
    #     if num_classes:
    #         if class_acc is None:
    #             class_acc = np.zeros((num_classes, 3))
    #         for cat in np.unique(target.cpu()):
    #             classacc = pred_choice.cpu()[target == cat].eq(target[target == cat].long()).cpu().sum()
    #
    #             val = float(data[target == cat].size()[0])
    #             if val > 0:
    #                 class_acc[cat, 0] += classacc.item() / val
    #                 class_acc[cat, 1] += 1
    #
    # instance_acc = np.mean(mean_correct)
    # if num_classes:
    #     class_acc[:, 2] = class_acc[:, 0] / class_acc[:, 1]
    #     class_acc = np.mean(class_acc[:, 2])
    #     laok.log_info(f"validate instance_acc:{instance_acc}, class_acc:{class_acc}")
    # else:
    #     laok.log_info(f"validate instance_acc:{instance_acc}")

    # return instance_acc, class_acc




