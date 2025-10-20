#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 14:29:40

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from .fwalk import *
#===============================================================================
r'''
'''
#===============================================================================
__all__ = ['suffix_image_list', 'suffix_dll_list', 'suffix_video_list',
           'image_cur', 'image_under',
           'video_cur', 'video_under',
           'dll_cur', 'dll_under',
           ]

def suffix_image_list():
    return [".bmp",".dib",	                # Windows位图文件
            ".jpeg",".jpg",".jpe",".jfif",	#JPEG文件
            ".png",	                        #便携式网络图片
            ".pbm",".pgm",".ppm",".pxm",".pnm",".pfm",	#便携式图像格式
            ".sr",".ras",	        #Sun rasters
            ".tiff",".tif",	        #TIFF文件
            ".exr",	                #OpenEXR HDR 图片
            ".hdr",
            ".pic",
            ".jp2",                 #JPEG 2000 图片
            ".webp"                 #WebP格式
            ]

def suffix_dll_list():
    return [".dll",".kll", ".so", ".pyd"]

def suffix_video_list():
    return [
        ".avi", # 音频视频交错(Audio Video Interleaved)AVI这个由微软公司发布的视频格式，在视频领域可以说是最悠久的格式之一。AVI格式调用方便、图像质量好，压缩标准可任意选择，是应用最广泛、也是应用时间最长的格式之一
        ".mpeg", ".mpg",  # Motion Picture Experts Group 的缩写。这类格式包括了MPEG-1,MPEG-2和MPEG-4在内的多种视频格式
        ".mov",  # MOV即QuickTime影片格式，它是Apple公司开发的一种音频、视频文件格式，用于存储常用数字媒体类型
        ".rm", ".ram",  # RealVideo视频格式是网络上的常用格式，对网络带宽要求比较低，能实现快速播放，但其视频画质没有其他格式视频高
        ".rmvb",  # RMVB是一种视频文件格式，其中的VB指Variable Bit Rate（可变比特率）。较上一代RM格式画面要清晰很多，原因是降低了静态画面下的比特率
        ".flv", ".swf",  # FLV是FLASH VIDEO的简称，FLV流媒体格式是一种新的视频格式。由于它形成的文件极小、加载速度极快，使得网络观看视频文件成为可能，
        ".mp4",  # MP4是一套用于音频、视频信息的压缩编码标准,MPEG-4格式的主要用途在于网上流、光盘、语音发送（视频电话），以及电视广播
        ".3gp",  # 3GP是第三代合作伙伴项目计划.为3G UMTS多媒体服务定义的一种多媒体容器格式，主要应用于3G移动电话，但也能在一些2G和4G手机上播放
        ".asf",  # (Advanced Streaming format高级流格式)。ASF 是MICROSOFT 为了和的Real player 竞争而发展出来的一种可以直接在网上观看视频节目的文件压缩格式
    ]

def image_cur(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_image_list()
    yield from files_cur(dir_names=dir_names, suffixes=suffixes)

def image_under(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_image_list()
    yield from files_under(dir_names=dir_names, suffixes=suffixes)

def video_cur(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_video_list()
    yield from files_cur(dir_names=dir_names, suffixes=suffixes)

def video_under(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_video_list()
    yield from files_under(dir_names=dir_names, suffixes=suffixes)

def dll_cur(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_dll_list()
    yield from files_cur(dir_names=dir_names, suffixes=suffixes)

def dll_under(dir_names, suffixes = None):
    if suffixes is None:
        suffixes = suffix_dll_list()
    yield from files_under(dir_names=dir_names, suffixes=suffixes)