#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2023/4/19 23:05:22
@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
from ..app import app
from flask import jsonify, request, g, session, current_app
#===============================================================================
r'''
'''
#===============================================================================

@app.route("/", methods=['POST', 'GET'])
def index():
    return jsonify(data = "Wellcom to laok's World!", status='success')

@app.errorhandler(404)
def not_found(error):
    return jsonify(data = 'not found', status='fail'), 404

@app.route('/debug', methods=['post', 'get', 'head', 'options', 'put', 'patch', 'delete'])
def requests():
    return jsonify(requests)
