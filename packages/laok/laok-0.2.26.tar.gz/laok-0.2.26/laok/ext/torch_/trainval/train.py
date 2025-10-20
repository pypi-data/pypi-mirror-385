#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/10/17 21:25:32

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
import laok
from tqdm import tqdm
from ..op.device import get_device
from .val import val_cls_dataloader
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['train_cls_batch', 'train_cls_dataloader', 'train_cls_epoches']

#################### 训练
def train_step(model, data, target, criterion, optimizer):
    optimizer.zero_grad()           # 优化器清空梯度
    pred = model(data)              # 执行推理
    loss = criterion(pred, target)  # 计算损失
    loss.backward()                 # 方向传播
    optimizer.step()                # 更新梯度
    return pred, loss

#################### 分类模型训练方式
def train_cls_batch(model, data, target, criterion, optimizer):
    _device = get_device(model)
    model.train()
    data, target = data.to(_device), target.to(_device)
    target = target.long() #转换成 long
    #训练
    pred, loss = train_step(model, data, target, criterion, optimizer)
    pred_choice = pred.max(1)[1]
    correct = pred_choice.eq(target).cpu().sum()
    return correct, loss.item()


def train_cls_dataloader(model, loader, criterion, optimizer):
    mean_correct = []
    mean_loss = []
    pbar = tqdm(enumerate(loader), total=len(loader), smoothing=0.9)

    for batch_id, (data, target) in pbar:
        d_size_str = laok.size_to_str(data.size())
        t_size_str = laok.size_to_str(target.size())
        pbar.set_description(f"train data:{d_size_str} target:{t_size_str}")
        correct, loss_value = train_cls_batch(model, data, target, criterion, optimizer)
        mean_correct.append(correct.item() / float(data.size()[0]))
        mean_loss.append(loss_value)

    _mean_correct = np.mean(mean_correct)
    _mean_loss = np.mean(mean_loss)
    laok.log_info(f"train instance_acc:{_mean_correct}  mean_loss:{_mean_loss}")
    return _mean_correct, _mean_loss


def train_cls_epoches(model, train_dataloader, criterion, optimizer, cpkt=None,
                      val_dataloader=None, epoches=100, num_classes=None,
                      lr_scheduler=None):

    for epoch in range(epoches):
        laok.log_info(f'====={epoch+1}/{epoches}')
        ins_acc, mean_loss = train_cls_dataloader(model, train_dataloader, criterion, optimizer)

        if val_dataloader:
            ins_acc, class_acc = val_cls_dataloader(model, val_dataloader, num_classes)

        if cpkt:
            cpkt.update(ins_acc)

        if lr_scheduler:
            lr_scheduler.step()

####################    分割模型训练





####################    检测模型训练














