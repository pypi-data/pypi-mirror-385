#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/9/17 23:37:17

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import os
import json
import numpy as np
from torch.utils.data import Dataset
import laok.util.log as klog
import laok.util.fs as kfs
import laok.util.parallel as kparal
import laok.cv3d as kcv3
# ===============================================================================
r'''
'''
# ===============================================================================

class ModelnetIneratia(Dataset):
    def __init__(self, root, split='train',
                 num_point = 1024,
                 num_category = 40,
                 transforms=None,
                 cached=False,
                 show_info = False,
                 ):
        self.root = root
        self.npoints = num_point
        self.num_category = num_category
        self.transforms = transforms
        self.split = split
        klog.debug(f'===== {self.__class__.__name__}')
        klog.debug(f'root={root}')
        klog.debug(f'split={split}, num_point={num_point}, num_category={num_category}')

        if self.num_category == 10:
            self.catfile = os.path.join(self.root, 'modelnet10_shape_names.txt')
        else:
            self.catfile = os.path.join(self.root, 'modelnet40_shape_names.txt')

        klog.debug(f'catfile={self.catfile}')

        self.cat = [line.rstrip() for line in open(self.catfile)]
        self.classes = dict(zip(self.cat, range(len(self.cat))))

        klog.debug(f'cat={self.cat}')
        klog.debug(f'classes={self.classes}')

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
        print('The size of %s data is %d' % (split, len(self.datapath)))
        self.show_info = show_info

    def __len__(self):
        return len(self.datapath)

    def _get_item(self, index):
        name, ptfile = self.datapath[index]

        if self.show_info:
            klog.info(f'{name} point-file:{ptfile}')

        cls = self.classes[name]
        label = np.array([cls]).astype(np.int32)

        point_set = np.loadtxt(ptfile, delimiter=',').astype(np.float32)
        # point_set = kcv3.farthest_point_sample(point_set, self.npoints)
        if self.split == 'train':
            point_set = kcv3.random_sample(point_set, self.npoints)
        else:
            point_set = point_set[:self.npoints, :]

        point_set[:, 0:3] = kcv3.pc_normalize(point_set[:, 0:3])

        interia_file = kfs.path_replace_ext(ptfile, 'inertia')
        if self.show_info:
            klog.info(f'interia_file: {interia_file}')

        with open(interia_file) as f:
            jdata = json.load(f)
            eccentricity = np.array(jdata['Eccentricity'], dtype=np.float32)
            interia = np.array(jdata['MomentOfInertia'], dtype=np.float32)

        if self.transforms:
            point_set = self.transforms(point_set)

        return point_set, label[0], interia, eccentricity

    def __getitem__(self, index):
        '''
        :param index:
        :return:  point_set, label, interia, eccentricity
        '''
        return self._get_item(index)


if __name__ == '__main__':
    import torch
    import laok.util.torch_ as ktorch
    import laok.util.conf as kconf

    data = ModelnetIneratia(kconf.get_conf('datasets').ModelnetIneratia,  num_point=1024, show_info=True, cached=True)
    # DataLoader = torch.utils.data.DataLoader(data, batch_size=2, shuffle=False)
    # for point, label, interia, eccentricity in DataLoader:
    #     ktorch.pr(point)
    #     ktorch.pr(label)
    #     ktorch.pr(interia)
    #     ktorch.pr(eccentricity)
    #     kcv3.show_cld_xyz(point[0])
    #     break
