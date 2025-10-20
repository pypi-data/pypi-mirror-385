#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/28 15:25:04

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from lxml import etree, objectify
from laok.base.fs import file_read_text, file_write_text, path_exist, file_read_bin, path_replace_ext
#===============================================================================
r'''
'''
#===============================================================================

__all__ = ['load_html', 'load_html_text', 'load_html_url',
           'load_xml', 'load_xml_text',
           'save_xml']

def load_html(filename, **kws):
    text = file_read_text(filename)
    return load_html_text(text, **kws)

def load_html_text(text, **kws):
    return etree.HTML(text, **kws)

def load_html_url(url, cache_file=None, **kws):
    from laok.ext.requests_ import req_text
    if cache_file:
        if path_exist(cache_file):
            text = file_read_text(cache_file)
        else:
            text = req_text(url, **kws)
            file_write_text(cache_file, text)
    else:
        text = req_text(url, **kws)
    base_url = kws.pop('base_url', None)
    return load_html_text(text, base_url)


def load_xml(filename, **kws):
    text = file_read_bin(filename)
    return load_xml_text(text, **kws)

def load_xml_text(text, **kws):
    return etree.XML(text, **kws)


def save_xml(filename, data, fix_ext=True, **kws):
    if isinstance(data, str):
        data = etree.XML(data)

    if isinstance(data, etree._Element):
        data = etree.ElementTree(data)

    if isinstance(data, objectify.ObjectifiedElement):
        data = etree.ElementTree(data)

    if isinstance(data, etree._ElementTree):
        kws.setdefault('encoding', 'utf8')
        kws.setdefault('pretty_print', True)
        if fix_ext:
            filename = path_replace_ext(filename, ".xml")
        data.write(filename, xml_declaration=True, **kws)
        return True
