#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/9/17 23:37:17

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
import numpy as np
from torch.utils.data import Dataset
from laok import log_info
# ===============================================================================
r'''
'''
# ===============================================================================

class Modelnet(Dataset):
    def __init__(self, root, split='train', num_point=1024, num_category=40, transforms=None, cached=False, show_info=False):
        self.root = root
        self.npoints = num_point
        self.num_category = num_category
        self.transforms = transforms
        self.split = split

        log_info(f'===== {self.__class__.__name__}')
        log_info(f'root={root}')
        log_info(f'split={split}, num_point={num_point}, num_category={num_category}')

        if self.num_category == 10:
            self.catfile = os.path.join(self.root, 'modelnet10_shape_names.txt')
        else:
            self.catfile = os.path.join(self.root, 'modelnet40_shape_names.txt')

        log_info(f'catfile={self.catfile}')

        self.cat = [line.rstrip() for line in open(self.catfile)]
        self.classes = dict(zip(self.cat, range(len(self.cat))))

        log_info(f'cat={self.cat}')
        log_info(f'classes={self.classes}')

        shape_ids = {}
        if self.num_category == 10:
            shape_ids['train'] = [line.rstrip() for line in open(os.path.join(self.root, 'modelnet10_train.txt'))]
            shape_ids['test'] = [line.rstrip() for line in open(os.path.join(self.root, 'modelnet10_test.txt'))]
        else:
            shape_ids['train'] = [line.rstrip() for line in open(os.path.join(self.root, 'modelnet40_train.txt'))]
            shape_ids['test'] = [line.rstrip() for line in open(os.path.join(self.root, 'modelnet40_test.txt'))]

        assert (split == 'train' or split == 'test')
        shape_names = ['_'.join(x.split('_')[0:-1]) for x in shape_ids[split]]
        self.datapath = [(shape_names[i], os.path.join(self.root, shape_names[i], shape_ids[split][i]) + '.txt') for i
                         in range(len(shape_ids[split]))]
        log_info(f'The size of {split} data is {len(self.datapath)}')
        self.show_info = show_info

    def __len__(self):
        return len(self.datapath)

    def _get_item(self, index):
        name, fname = self.datapath[index]
        cls = self.classes[name]
        label = np.array([cls]).astype(np.int32)
        if self.show_info:
            log_info(f'load {fname}')
        point_set = np.loadtxt(fname, delimiter=',').astype(np.float32)
        # point_set = kcv3.farthest_point_sample(point_set, self.npoints)
        if self.split == 'train':
            point_set = kcv3.random_sample(point_set, self.npoints)
        else:
            point_set = point_set[:self.npoints, :]

        point_set[:, 0:3] = kcv3.pc_normalize(point_set[:, 0:3])
        if self.transforms:
            point_set = self.transforms(point_set)
        return point_set, label[0]

    def __getitem__(self, index):
        return self._get_item(index)

if __name__ == '__main__':
    import torch
    import laok.util.torch_ as ktorch
    import laok.util.conf as kconf

    dataset = Modelnet(kconf.get_conf('datasets').Modelnet ,  num_point=1024, show_info=True, cached=True)
    # DataLoader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=False)
    # for point, label in dataset:
    #     ktorch.pr(point)
    #     ktorch.pr(label)

    #     kcv3.show_cld_xyz(point[0])
    #     break
