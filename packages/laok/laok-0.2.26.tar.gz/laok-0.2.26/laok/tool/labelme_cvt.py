#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/12/21 00:28:06

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from lxml import etree
import json, base64
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['voc_to_labelme']

def voc_to_labelme(xml_file, needImageData = False):
    with open(xml_file, mode='rb') as f:
        xml_data = etree.XML(f.read())
    jdata = {}
    jdata['version'] = "5.0.1"
    jdata["flags"] = {}
    shapes = []
    for obj in xml_data.findall('object'):
        name = obj.find('name').text
        xmin = int(obj.find('bndbox/xmin').text)
        ymin = int(obj.find('bndbox/ymin').text)
        xmax = int(obj.find('bndbox/xmax').text)
        ymax = int(obj.find('bndbox/ymax').text)
        shapes.append({
            "label": name,
            "points":[
                [ xmin, ymin ],
                [ xmax, ymax ]
            ],
            "group_id": {},
            "shape_type": "rectangle",
            "flags": {}
        })
    jdata['shapes'] = shapes

    imagePath = xml_data.find('filename').text
    jdata['imagePath'] = imagePath
    width = xml_data.find('size/width').text
    height = xml_data.find('size/height').text

    if needImageData:
        with open(imagePath, 'rb') as f:
            imageData = f.read()
        jdata['imageData'] = base64.b64encode(imageData).decode('utf-8')
    else:
        jdata['imageData'] = None
    jdata['imageHeight'] = int(height)
    jdata['imageWidth'] = int(width)

    json_file = xml_file.replace('.xml', '.json')
    with open(json_file, 'w', encoding='utf8') as wf:
        json.dump(jdata, wf, indent=2)
    return jdata
