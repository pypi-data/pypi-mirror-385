#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/2 22:28:48

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from sklearn import cluster
from sklearn import mixture
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = [
 'ClusterAffinityPropagation',
 'ClusterAgglomerative',
 'ClusterBayesianGaussianMixture',
 'ClusterBirch',
 'ClusterBisectingKMeans',
 'ClusterDBSCAN',
 'ClusterGaussianMixture',
 'ClusterKMeans',
 'ClusterMeanShift',
 'ClusterMiniBatchKMeans',
 'ClusterOPTICS',
 'ClusterSpectral',
 'ClusterSpectralBi',
 'ClusterSpectralCo']

# cluster
ClusterAffinityPropagation = cluster.AffinityPropagation
ClusterAgglomerative = cluster.AgglomerativeClustering
ClusterBirch = cluster.Birch
ClusterDBSCAN = cluster.DBSCAN
ClusterKMeans = cluster.KMeans
ClusterBisectingKMeans = cluster.BisectingKMeans
ClusterMiniBatchKMeans = cluster.MiniBatchKMeans
ClusterMeanShift = cluster.MeanShift
ClusterOPTICS = cluster.OPTICS
ClusterSpectral = cluster.SpectralClustering
ClusterSpectralCo = cluster.SpectralCoclustering
ClusterSpectralBi = cluster.SpectralBiclustering

# mixture
ClusterGaussianMixture = mixture.GaussianMixture
ClusterBayesianGaussianMixture = mixture.BayesianGaussianMixture
