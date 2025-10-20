#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2025/5/15 14:11:25

@author: Liu Kuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
import torch
from tqdm import tqdm
# ===============================================================================
r'''
'''
# ===============================================================================


def test(model, loader, num_class=40, use_cpu=True):
    mean_correct = []
    class_acc = np.zeros((num_class, 3))
    classifier = model.eval()

    for j, (points, target) in tqdm(enumerate(loader), total=len(loader)):

        if not use_cpu:
            points, target = points.cuda(), target.cuda()

        points = points.transpose(2, 1)
        pred, _ = classifier(points)
        pred_choice = pred.data.max(1)[1]

        for cat in np.unique(target.cpu()):
            classacc = pred_choice[target == cat].eq(target[target == cat].long().data).cpu().sum()
            class_acc[cat, 0] += classacc.item() / float(points[target == cat].size()[0])
            class_acc[cat, 1] += 1

        correct = pred_choice.eq(target.long().data).cpu().sum()
        mean_correct.append(correct.item() / float(points.size()[0]))

    class_acc[:, 2] = class_acc[:, 0] / class_acc[:, 1]
    class_acc = np.mean(class_acc[:, 2])
    instance_acc = np.mean(mean_correct)

    return instance_acc, class_acc


val = '-0.24453,-0.570776,-0.78385'
x,y,z = [float(x) for x in val.split(',')]
print('len=', x*x + y*y + z*z)