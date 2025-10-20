#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/3 21:26:54

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
from sklearn import datasets
# ===============================================================================
r'''数据集定义
'''
# ===============================================================================
__all__ = [
 'data_make_biclusters',
 'data_make_blobs',
 'data_make_checkerboard',
 'data_make_circles',
 'data_make_classification',
 'data_make_friedman1',
 'data_make_friedman2',
 'data_make_friedman3',
 'data_make_gaussian_quantiles',
 'data_make_hastie_10_2',
 'data_make_low_rank_matrix',
 'data_make_moons',
 'data_make_multilabel_classification',
 'data_make_regression',
 'data_make_s_curve',
 'data_make_sparse_coded_signal',
 'data_make_sparse_spd_matrix',
 'data_make_sparse_uncorrelated',
 'data_make_spd_matrix',
 'data_make_swiss_roll',


 'data_breast_cancer',
 'data_diabetes',
 'data_digits',
 'data_files',
 'data_iris',
 'data_linnerud',
 'data_sample_image',
 'data_sample_images',
 'data_svmlight_file',
 'data_svmlight_files',
 'data_wine',
]



data_make_biclusters = datasets.make_biclusters
data_make_blobs = datasets.make_blobs
data_make_checkerboard = datasets.make_checkerboard
data_make_circles = datasets.make_circles
data_make_classification = datasets.make_classification
data_make_friedman1 = datasets.make_friedman1
data_make_friedman2 = datasets.make_friedman2
data_make_friedman3 = datasets.make_friedman3
data_make_gaussian_quantiles = datasets.make_gaussian_quantiles
data_make_hastie_10_2 = datasets.make_hastie_10_2
data_make_low_rank_matrix = datasets.make_low_rank_matrix
data_make_moons = datasets.make_moons
data_make_multilabel_classification = datasets.make_multilabel_classification
data_make_regression = datasets.make_regression
data_make_s_curve = datasets.make_s_curve
data_make_sparse_coded_signal = datasets.make_sparse_coded_signal
data_make_sparse_spd_matrix = datasets.make_sparse_spd_matrix
data_make_sparse_uncorrelated = datasets.make_sparse_uncorrelated
data_make_spd_matrix = datasets.make_spd_matrix
data_make_swiss_roll = datasets.make_swiss_roll

data_breast_cancer = datasets.load_breast_cancer
data_diabetes = datasets.load_diabetes
data_digits = datasets.load_digits
data_files = datasets.load_files
data_iris = datasets.load_iris
data_linnerud = datasets.load_linnerud
data_sample_image = datasets.load_sample_image
data_sample_images = datasets.load_sample_images
data_svmlight_file = datasets.load_svmlight_file
data_svmlight_files = datasets.load_svmlight_files
data_wine = datasets.load_wine


