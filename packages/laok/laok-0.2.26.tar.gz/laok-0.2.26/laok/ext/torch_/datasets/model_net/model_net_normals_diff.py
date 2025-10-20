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
import laok.util.log as klog
import laok.util.fs as kfs
import laok.util.parallel as kparal
import laok.cv3d as kcv3
# ===============================================================================
r'''
'''
# ===============================================================================

class ModelnetNormalsDiff(Dataset):
    def __init__(self, root, split='train',
                 num_point = 1024,
                 num_category = 40,
                 normal_small_knn = 3,
                 normal_large_knn = 6,
                 transform=None,
                 cached = False,
                 show_info = False,
                 ):
        self.root = root
        self.npoints = num_point
        self.num_category = num_category
        self.transform = transform
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

        self._cache = {}
        self.normal_small_knn = normal_small_knn
        self.normal_large_knn = normal_large_knn
        self.show_info = show_info

    def __len__(self):
        return len(self.datapath)

    def _get_item(self, index):
        name, ptfile = self.datapath[index]

        if self.show_info:
            klog.info(f'{name} {ptfile}')

        cls = self.classes[name]
        label = np.array([cls]).astype(np.int32)
        point_set = np.loadtxt(ptfile, delimiter=',').astype(np.float32)

        normal_samll_file = ptfile.replace('.txt', "-%02d.normals" % self.normal_small_knn)
        if self.show_info:
            klog.info(f'normal_samll_file: {normal_samll_file}')
        normal_small_set = np.loadtxt(normal_samll_file, delimiter=',').astype(np.float32)

        normal_large_file = ptfile.replace('.txt', "-%02d.normals" % self.normal_large_knn)
        if self.show_info:
            klog.info(f'normal_large_file: {normal_large_file}')
        normal_large_set = np.loadtxt(normal_large_file, delimiter=',').astype(np.float32)

        normal_set = (normal_small_set - normal_large_set) / 2
        point_set = np.concatenate([point_set[:, 0:3], normal_set], axis=1)
        # point_set = kcv3.farthest_point_sample(point_set, self.npoints)
        if self.split == 'train':
            point_set = kcv3.random_sample(point_set, self.npoints)
        else:
            point_set = point_set[:self.npoints, :]

        point_set[:, 0:3] = kcv3.pc_normalize(point_set[:, 0:3])

        if self.transform:
            point_set = self.transform(point_set)
        return point_set, label[0]

    def __getitem__(self, index):
        '''
        :param index:
        :return:  point_set, label
        '''
        return self._get_item(index)


if __name__ == '__main__':
    import laok.util.conf as kconf
    data = ModelnetNormalsDiff(kconf.get_conf('datasets').ModelnetNormals,  num_point=1024, show_info=True, cached=True)

