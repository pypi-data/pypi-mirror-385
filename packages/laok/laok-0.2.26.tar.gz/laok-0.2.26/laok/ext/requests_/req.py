#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 19:43:45
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import requests
from laok.base.fs import file_write_bin, path_exist
from laok.base.net import url_make_file
#===============================================================================
r'''requests工具代码
'''
#===============================================================================
__all__ = ['random_user_agent', 'req', 'req_text', 'req_json', 'req_content', 'req_save', 'req_save_auto']

_random_user_agent = False
def random_user_agent():
    ''' 拦截请求的参数,将headers修改为 自定义的 user_agent
    :return:
    '''
    global _random_user_agent
    if _random_user_agent:
        return
    _random_user_agent = True
    user_agent_pc = [
        # 谷歌
        'Mozilla/5.0.html (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.html.2171.71 Safari/537.36',
        'Mozilla/5.0.html (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.html.1271.64 Safari/537.11',
        'Mozilla/5.0.html (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.html.648.133 Safari/534.16',
        # 火狐
        'Mozilla/5.0.html (Windows NT 6.1; WOW64; rv:34.0.html) Gecko/20100101 Firefox/34.0.html',
        'Mozilla/5.0.html (X11; U; Linux x86_64; zh-CN; rv:1.9.2.10) Gecko/20100922 Ubuntu/10.10 (maverick) Firefox/3.6.10',
        # opera
        'Mozilla/5.0.html (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.html.2171.95 Safari/537.36 OPR/26.0.html.1656.60',
        # qq浏览器
        'Mozilla/5.0.html (compatible; MSIE 9.0.html; Windows NT 6.1; WOW64; Trident/5.0.html; SLCC2; .NET CLR 2.0.html.50727; .NET CLR 3.5.30729; .NET CLR 3.0.html.30729; Media Center PC 6.0.html; .NET4.0C; .NET4.0E; QQBrowser/7.0.html.3698.400)',
        # 搜狗浏览器
        'Mozilla/5.0.html (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.html.963.84 Safari/535.11 SE 2.X MetaSr 1.0.html',
        # 360浏览器
        'Mozilla/5.0.html (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.html.1599.101 Safari/537.36',
        'Mozilla/5.0.html (Windows NT 6.1; WOW64; Trident/7.0.html; rv:11.0.html) like Gecko',
        # uc浏览器
        'Mozilla/5.0.html (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.html.2125.122 UBrowser/4.0.html.3214.0.html Safari/537.36',
    ]
    import random
    _req = requests.Session.request
    def user_agent_req(*args, **kwargs):
        headers = kwargs.get('headers')
        if not headers:
            headers = {}
        headers['User-Agent'] = random.choice(user_agent_pc)
        kwargs['headers'] = headers
        return _req(*args, **kwargs)
    requests.Session.request = user_agent_req

def req(url, method='get', **kws):
    '''设置随机 user-agent,然后执行请求
    '''
    random_user_agent()
    return requests.request(method=method, url=url, **kws)

def req_text(url, method='get', **kws):
    '''返回 text '''
    return req(url=url, method=method, **kws).text

def req_json(url, method='get', **kws):
    '''返回 json '''
    return req(url=url, method=method, **kws).json()

def req_content(url, method='get', **kws):
    '''返回二进制内容'''
    return req(url=url, method=method, **kws).content

def req_save(fname, url, method='get', skip_exist=False, **kws):
    '''baocun数据'''
    if skip_exist and path_exist(fname):
        return fname
    data = req_content(url=url, method=method, **kws)
    file_write_bin(fname, data)
    return fname

def req_save_auto(url, method='get', skip_exist=False, **kws):
    fname = url_make_file(url)
    req_save(fname=fname, url=url, method=method, skip_exist=skip_exist, **kws)
    return fname

