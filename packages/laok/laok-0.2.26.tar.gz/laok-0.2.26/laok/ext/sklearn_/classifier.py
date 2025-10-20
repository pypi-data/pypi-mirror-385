#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 22:28:29

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import linear_model
from sklearn import discriminant_analysis
from sklearn import svm
from sklearn import neighbors
from sklearn import gaussian_process
from sklearn import naive_bayes
from sklearn import tree
from sklearn import ensemble
from sklearn import neural_network
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = [
 'ClassifierAdaBoost',
 'ClassifierBagging',
 'ClassifierBernoulliNB',
 'ClassifierCategoricalNB',
 'ClassifierComplementNB',
 'ClassifierDecisionTree',
 'ClassifierExtraTree',
 'ClassifierExtraTrees',
 'ClassifierGaussianNB',
 'ClassifierGaussianProcess',
 'ClassifierGradientBoosting',
 'ClassifierHistGradientBoosting',
 'ClassifierIsolationForest',
 'ClassifierKNeighbors',
 'ClassifierLDA',
 'ClassifierLinearSVC',
 'ClassifierLogisticRegression',
 'ClassifierLogisticRegressionCV',
 'ClassifierMLP',
 'ClassifierMultinomialNB',
 'ClassifierNearestCentroid',
 'ClassifierNuSVC',
 'ClassifierOneClassSVM',
 'ClassifierPassiveAggressive',
 'ClassifierPerceptron',
 'ClassifierQDA',
 'ClassifierRadiusNeighbors',
 'ClassifierRandomForest',
 'ClassifierRidge',
 'ClassifierSGD',
 'ClassifierSGDOneClassSVM',
 'ClassifierSVC',
 'ClassifierStacking',
 'ClassifierVoting',
 ]

# linear_model
ClassifierRidge = linear_model.RidgeClassifier
ClassifierLogisticRegression = linear_model.LogisticRegression
ClassifierLogisticRegressionCV = linear_model.LogisticRegressionCV
ClassifierSGD = linear_model.SGDClassifier
ClassifierPerceptron = linear_model.Perceptron
ClassifierPassiveAggressive = linear_model.PassiveAggressiveClassifier
ClassifierSGDOneClassSVM = linear_model.SGDOneClassSVM


# discriminant_analysis
ClassifierLDA = discriminant_analysis.LinearDiscriminantAnalysis
ClassifierQDA = discriminant_analysis.QuadraticDiscriminantAnalysis

# svm
ClassifierSVC = svm.SVC
ClassifierNuSVC = svm.NuSVC
ClassifierLinearSVC = svm.LinearSVC
ClassifierOneClassSVM = svm.OneClassSVM

# neighbors
ClassifierKNeighbors = neighbors.KNeighborsClassifier
ClassifierRadiusNeighbors = neighbors.RadiusNeighborsClassifier
ClassifierNearestCentroid = neighbors.NearestCentroid

# gaussian_process
ClassifierGaussianProcess = gaussian_process.GaussianProcessClassifier

# naive_bayes
ClassifierBernoulliNB = naive_bayes.BernoulliNB
ClassifierGaussianNB = naive_bayes.GaussianNB
ClassifierMultinomialNB = naive_bayes.MultinomialNB
ClassifierComplementNB = naive_bayes.ComplementNB
ClassifierCategoricalNB = naive_bayes.CategoricalNB

# tree
ClassifierDecisionTree = tree.DecisionTreeClassifier
ClassifierExtraTree = tree.ExtraTreeClassifier

# ensemble
ClassifierRandomForest = ensemble.RandomForestClassifier
ClassifierExtraTrees = ensemble.ExtraTreesClassifier
ClassifierBagging = ensemble.BaggingClassifier
ClassifierIsolationForest = ensemble.IsolationForest
ClassifierGradientBoosting = ensemble.GradientBoostingClassifier
ClassifierAdaBoost = ensemble.AdaBoostClassifier
ClassifierVoting = ensemble.VotingClassifier
ClassifierStacking = ensemble.StackingClassifier
ClassifierHistGradientBoosting = ensemble.HistGradientBoostingClassifier

# neural_network
ClassifierMLP = neural_network.MLPClassifier

