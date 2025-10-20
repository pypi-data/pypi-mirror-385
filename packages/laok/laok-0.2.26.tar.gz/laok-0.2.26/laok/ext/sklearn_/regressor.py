#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 22:28:18

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import linear_model
from sklearn import svm
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = [
 'RegressorARD',
 'RegressorBayesianRidge',
 'RegressorElasticNet',
 'RegressorElasticNetCV',
 'RegressorHuber',
 'RegressorLasso',
 'RegressorLassoCV',
 'RegressorLassoLars',
 'RegressorLassoLarsCV',
 'RegressorLinear',
 'RegressorLinearSVR',
 'RegressorMultiTaskElasticNet',
 'RegressorMultiTaskElasticNetCV',
 'RegressorMultiTaskLasso',
 'RegressorMultiTaskLassoCV',
 'RegressorNuSVR',
 'RegressorPassiveAggressive',
 'RegressorRANSAC',
 'RegressorRidge',
 'RegressorRidgeCV',
 'RegressorSGD',
 'RegressorSVR',
 'RegressorTheilSen']


# linear_model
RegressorLinear = linear_model.LinearRegression

RegressorRidge = linear_model.Ridge
RegressorRidgeCV = linear_model.RidgeCV

RegressorLasso = linear_model.Lasso
RegressorLassoCV = linear_model.LassoCV
RegressorMultiTaskLasso = linear_model.MultiTaskLasso
RegressorMultiTaskLassoCV = linear_model.MultiTaskLassoCV

RegressorElasticNet = linear_model.ElasticNet
RegressorElasticNetCV = linear_model.ElasticNetCV
RegressorMultiTaskElasticNet = linear_model.MultiTaskElasticNet
RegressorMultiTaskElasticNetCV = linear_model.MultiTaskElasticNetCV

RegressorLassoLars = linear_model.LassoLars
RegressorLassoLarsCV = linear_model.LassoLarsCV

RegressorBayesianRidge = linear_model.BayesianRidge

RegressorARD = linear_model.ARDRegression

RegressorSGD = linear_model.SGDRegressor

RegressorPassiveAggressive = linear_model.PassiveAggressiveRegressor

RegressorRANSAC = linear_model.RANSACRegressor

RegressorTheilSen = linear_model.TheilSenRegressor

RegressorHuber = linear_model.HuberRegressor

# svm
RegressorNuSVR = svm.NuSVR
RegressorSVR = svm.SVR
RegressorLinearSVR = svm.LinearSVR

