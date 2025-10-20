#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/5/23 16:25:29

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import socket
#===============================================================================
'''     
'''
#===============================================================================
__all__ = ['get_ip']

def get_ip():
    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        st.close()
    return IP

if __name__ == '__main__':
    print('get_ip =', get_ip())
