#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 23:04:07

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import metrics
# ===============================================================================
r'''评分函数
'''
# ===============================================================================
__all__ = ['score_accuracy',
 'score_adjusted_mutual_info',
 'score_adjusted_rand',
 'score_average_precision',
 'score_balanced_accuracy',
 'score_calinski_harabasz',
 'score_cohen_kappa',
 'score_completeness',
 'score_consensus',
 'score_d2_absolute_error',
 'score_d2_pinball',
 'score_d2_tweedie',
 'score_davies_bouldin',
 'score_dcg',
 'score_explained_variance',
 'score_f1',
 'score_fbeta',
 'score_fowlkes_mallows',
 'score_homogeneity',
 'score_jaccard',
 'score_label_ranking_average_precision',
 'score_mutual_info',
 'score_ndcg',
 'score_normalized_mutual_info',
 'score_precision',
 'score_r2',
 'score_rand',
 'score_recall',
 'score_roc_auc',
 'score_silhouette',
 'score_top_k_accuracy',
 'score_v_measure']



score_accuracy = metrics.accuracy_score
score_adjusted_mutual_info = metrics.adjusted_mutual_info_score
score_adjusted_rand = metrics.adjusted_rand_score
score_average_precision = metrics.average_precision_score
score_balanced_accuracy = metrics.balanced_accuracy_score
score_calinski_harabasz = metrics.calinski_harabasz_score
score_cohen_kappa = metrics.cohen_kappa_score
score_completeness = metrics.completeness_score
score_consensus = metrics.consensus_score
score_d2_absolute_error = metrics.d2_absolute_error_score
score_d2_pinball = metrics.d2_pinball_score
score_d2_tweedie = metrics.d2_tweedie_score
score_davies_bouldin = metrics.davies_bouldin_score
score_dcg = metrics.dcg_score
score_explained_variance = metrics.explained_variance_score
score_f1 = metrics.f1_score
score_fbeta = metrics.fbeta_score
score_fowlkes_mallows = metrics.fowlkes_mallows_score
score_homogeneity = metrics.homogeneity_score
score_jaccard = metrics.jaccard_score
score_label_ranking_average_precision = metrics.label_ranking_average_precision_score
score_mutual_info = metrics.mutual_info_score
score_ndcg = metrics.ndcg_score
score_normalized_mutual_info = metrics.normalized_mutual_info_score
score_precision = metrics.precision_score
score_r2 = metrics.r2_score
score_rand = metrics.rand_score
score_recall = metrics.recall_score
score_roc_auc = metrics.roc_auc_score
score_silhouette = metrics.silhouette_score
score_top_k_accuracy = metrics.top_k_accuracy_score
score_v_measure = metrics.v_measure_score



