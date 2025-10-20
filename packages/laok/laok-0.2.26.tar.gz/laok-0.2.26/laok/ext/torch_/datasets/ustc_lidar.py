#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/9/17 23:37:17

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import numpy as np
from torch.utils.data import Dataset
import laok.util.log as klog
from laok.cv3d.transform.sample import sample_cld_random, sample_cld_index
import laok.util.fs as kfs
# ===============================================================================
r'''
'''
# ===============================================================================

class UstcLidar(Dataset):

    def __init__(self, root, train=True, num_point=3000, transform=None, show_info=True):
        self.root = root
        self.num_point = num_point
        self.show_info = show_info
        self.transform = transform
        self.show_info = show_info
        self.train = train

        if show_info:
            klog.debug(f'===== {self.__class__.__name__}')
            klog.debug(f'train={train}, root={root}, transform={transform}')
            klog.debug(f'num_point={num_point}, show_info={show_info}')

        cat = []
        datapath = {}
        idx = 0
        for i, dirname in enumerate(kfs.dirs_cur(root)):
            name = kfs.path_stem(dirname).split('_')[1]
            cat.append(name)
            for fname in kfs.files_under(dirname, '.bin'):
                datapath[idx] = (i, fname)
                idx += 1

        self.datapath = datapath
        self.cat = cat
        self.classes = dict(zip(self.cat, range(len(self.cat))))

        if self.show_info:
            klog.debug(f'the size of data is {len(self.datapath)}, num_classes={len(self.classes)}')
            klog.debug(f'classes={self.classes}')

    def __len__(self):
        return len(self.datapath)

    def _get_item(self, index):
        cls, fname = self.datapath[index]
        label = np.array([cls]).astype(np.int32)

        # if self.show_info:
        #     klog.info(f'load {fname}')

        point_set = np.fromfile(fname, dtype=np.float32).reshape(-1, 4)

        if self.train:
            point_set = sample_cld_random(point_set, self.num_point)
        else:
            point_set = sample_cld_index(point_set, self.num_point)

        if self.transform:
            point_set = self.transform(point_set)

        return point_set, label[0]

    def __getitem__(self, index):
        return self._get_item(index)

# if __name__ == '__main__':
#     import torch
#     import laok.util.torch_ as ktorch
#     import laok.util.conf as kconf
#
#     dataset = UstcLidar(kconf.get_conf('datasets').Ustc,  num_point=3000, show_info=False)
#     dataloader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=False)
#     for point, label in dataloader:
#         ktorch.pr(point)
#         ktorch.pr(label)
#
#         kcv3.show_cld_xyz(point[0])
#         break
