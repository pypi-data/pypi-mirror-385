#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/3 22:56:24

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import preprocessing
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['TransStandardScaler',

           ]

# function
TransFunction = preprocessing.FunctionTransformer

# data
TransBinarizer = preprocessing.Binarizer
TransKernelCenterer = preprocessing.KernelCenterer
TransMaxAbsScaler = preprocessing.MaxAbsScaler
TransNormalizer = preprocessing.Normalizer
TransRobustScaler = preprocessing.RobustScaler
TransStandardScaler = preprocessing.StandardScaler
TransQuantile = preprocessing.QuantileTransformer
TransPower = preprocessing.PowerTransformer

trans_add_dummy = preprocessing.add_dummy_feature
trans_binarize = preprocessing.binarize
trans_normalize = preprocessing.normalize
trans_scale = preprocessing.scale
trans_robust_scale = preprocessing.robust_scale
trans_maxabs_scale = preprocessing.maxabs_scale
trans_minmax_scale = preprocessing.minmax_scale
trans_quantile = preprocessing.quantile_transform
trans_power = preprocessing.power_transform

# encode
TransEncoderOneHot = preprocessing.OneHotEncoder
TransEncoderOrdinal = preprocessing.OrdinalEncoder

# label
TransLabelBinarizer = preprocessing.LabelBinarizer
TransLabelEncoder = preprocessing.LabelEncoder
TransLabelMultiEncoder = preprocessing.MultiLabelBinarizer

trans_label_binarize = preprocessing.label_binarize

# discretization
TransKBinsDiscretizer = preprocessing.KBinsDiscretizer

# polynomial
TransPolyFeatures = preprocessing.PolynomialFeatures
TransPolySpline = preprocessing.SplineTransformer

