#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/7/12 14:48:16

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import cv2

# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['contour_extract_external', 'contour_extract_list', 'contour_extract_twolevel',

           ]

def contour_extract_external(img, method = cv2.CHAIN_APPROX_SIMPLE):
    contours, hierarchy = cv2.findContours(img, mode=cv2.RETR_EXTERNAL, method=method)
    return contours

def contour_extract_list(img, method = cv2.CHAIN_APPROX_SIMPLE):
    contours, hierarchy = cv2.findContours(img, mode=cv2.RETR_LIST, method=method)
    return contours

def contour_extract_twolevel(img, method = cv2.CHAIN_APPROX_SIMPLE):
    contours, hierarchy = cv2.findContours(img, mode=cv2.RETR_CCOMP, method=method)
    return contours

def contour_statis_area(contours):
    pass

def contour_statis_moment(contours):
    pass

def contour_fit_poly(contours):
    pass

def contour_fit_convex_hull(contours):
    pass

def contour_fit_ratate_rect(contours):
    pass

def contour_fit_bouding_rect(contours):
    pass

def contour_fit_min_enclose_circle(contours):
    pass

def contour_fit_ellipse(contours):
    pass

def contour_fit_line(contours):
    pass

def contour_filter_point_count():
    pass

def contour_filter_area():
    pass

def contour_filter_bounding_rect():
    pass











