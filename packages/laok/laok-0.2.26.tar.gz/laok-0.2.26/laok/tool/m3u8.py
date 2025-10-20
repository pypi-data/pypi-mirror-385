#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/8/3 11:00:32

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import laok
import laok.ext.requests_ as kreq
import laok.ext.Crypto_ as kcrypto
from collections import defaultdict
from tqdm import tqdm
# ===============================================================================
r'''
'''
# ===============================================================================
__all__ = [
            'ts_data_list_gen',
            'ts_data_list_filter',
            'ts_download',
            'ts_download_decrpyt',
            'ts_data_list_download',
            'ts_list_merge',
            'ts_download_m3u8'
           ]


# 下载 ts data list
# 存储为字典列表,内容有 url,key,iv,file
def ts_data_list_gen(url, del_cache=False):
    ts_data_list = []
    method = 'NONE'
    iv = b'0000000000000000'
    key = b''

    #保存 index文件
    index_file = kreq.req_save_auto(url, skip_exist=True)

    #保存 url
    url_file = laok.path_replace_basename(index_file, 'url.txt')
    laok.file_write_text(url_file, url, skip_exist=True)

    #读取index文件
    for line in laok.file_read_lines(index_file, skip_empty=True):
        if line.startswith('#EXT-X-KEY'):
            kdata = [v.strip() for v in line[11:].split(',')]
            method = 'NONE'
            iv = b'0000000000000000'
            key = b''
            for d in kdata:
                if d.startswith('METHOD='):
                    method = d[7:]
                elif d.startswith('URI='):
                    uri = laok.url_join(url, d[4:].strip('""') )
                    key_file = kreq.req_save_auto(uri, skip_exist=True)
                    key = laok.file_read_bin(key_file)
                    if del_cache:
                        laok.file_delete(key_file)
        elif line.startswith('#EXT-X-ENDLIST'):
            break
        elif line[0] != '#':
            uri = laok.url_join(url, line)
            ts_data_list.append({ 'url': uri,
                                  'key': key,
                                  'iv': iv,
                                  'method': method,
            })

    if del_cache:
        laok.file_delete(index_file)
        laok.file_delete(url_file)

    return ts_data_list

# 根据路径前缀过滤 插入的广告
def ts_data_list_filter(ts_list):
    prefix_dict = defaultdict(list)
    for ts in ts_list:
        prefix_dict[laok.path_parent(ts['url'])].append(ts)
    return max(prefix_dict.values(), key= lambda x : len(x) )


# 下载解密的 ts文件
def ts_download_decrpyt(url, key, iv):
    ts_file = laok.url_make_file(url)
    if laok.path_exist(ts_file):
        return ts_file
    kreq.req_save(ts_file, url)
    if key:
        kcrypto.aes_decrypt_cbc_file_(ts_file, key, iv)
    return ts_file

# 下载未解密的 ts文件
def ts_download(url):
    ts_file = laok.url_make_file(url)
    return kreq.req_save(ts_file, url, skip_exist=True)

# 下载 ts data list
# 从ts_data_list_gen/ts_data_list_filter 获取结果
def ts_data_list_download(ts_data_list, queue_size=100):
    pbar = tqdm(total=len(ts_data_list)+1)
    def download_ts_data(ts_data):
        pbar.set_description(ts_data['url'])
        pbar.update(1)
        return ts_download_decrpyt(ts_data['url'], ts_data['key'], ts_data['iv'])
    return laok.paral_seq(ts_data_list, download_ts_data, queue_size)

# 合并 ts_list 文件,并保存到 dst_file
# del_cache 是否删除缓冲文件
def ts_list_merge(ts_list, dst_file, del_cache=False):
    if len(ts_list) < 1:
        return

    dst_file = laok.path_replace_ext(dst_file, '.mp4')
    laok.file_list_merge(ts_list, dst_file)
    if not del_cache:
        return

    #删除所有ts
    for ts in ts_list:
        laok.file_delete(ts)

#下载 m3u8文件
def ts_download_m3u8(url, dst_file, queue_size=100, del_cache=False):
    ts_data_list = ts_data_list_gen(url, del_cache=del_cache)
    ts_data_list = ts_data_list_filter(ts_data_list)
    ts_list = ts_data_list_download(ts_data_list, queue_size=queue_size)
    ts_list_merge(ts_list, dst_file, del_cache=del_cache)

def convert_m3u8_mp4(index_file):

    pass

if __name__ == '__main__':
    import fire as _fire
    _fire.Fire(ts_download_m3u8)