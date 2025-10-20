#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/6/7 00:23:50

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import urllib.parse as _url_parse
from ..fs import path_join
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = ['url_join',  'url_split', 'url_make_file']

def url_join(base, url, allow_fragments=True):
    return _url_parse.urljoin(base, url, allow_fragments=allow_fragments)

def url_split(url, scheme='', allow_fragments=True):
    '''http://user:pwd@NetLoc:80/p1;para/p2;para?query=arg#frag
        scheme  : http
        netloc  : user:pwd@NetLoc:80
        path    : /p1;para/p2;para
        query   : query=arg
        fragment: frag
        username: user
        password: pwd
        hostname: netloc
        port    : 80
    '''
    return _url_parse.urlsplit(url, scheme, allow_fragments=allow_fragments)

def url_make_file(url):
    res = url_split(url)
    netloc = res.netloc
    path = res.path[1:]
    netloc = netloc.replace(':', '_')
    fname = path_join(netloc, path, make_parent=True)
    return fname
