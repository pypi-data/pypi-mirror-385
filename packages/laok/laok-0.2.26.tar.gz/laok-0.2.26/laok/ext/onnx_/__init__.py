#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2022/4/19 11:14:26

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import onnx
import onnxruntime
from laok.base.fs import path_replace_ext, path_exist
#===============================================================================
'''
'''
#===============================================================================
__all__ = ['check_model', 'load_model', 'dump_model_info']

def check_model(onnxFile):
    '''check onnx model if it is valide
    :param onnxFile:
    :return:
    '''
    model = onnx.load_model(onnxFile)
    onnx.checker.check_model(model)

def load_model(onnxFile):
    '''
    :param onnxFile:
    :return:
    '''
    return onnx.load_model(onnxFile)

def __fmt_node_arg(nodes):
    msg_list = []
    for node in nodes:
        shape_name = "(" + ", ".join( str(s) for s in node.shape) + ")"
        msg_list.append(f'    {node.name} : {shape_name} , type={node.type}')
    return msg_list

def dump_model_info(onnxFile, graphFile = None, skip_exist = False, show_info = True):
    '''
    :param onnxFile:
    :param graphFile:
    :param skip_exist:
    :param show_info:
    :return:
    '''
    if graphFile is None:
        graphFile = path_replace_ext(onnxFile, '.graph')

    if skip_exist and path_exist(graphFile):
        return graphFile

    if show_info:
        print(f'start read... {onnxFile}')

    msg_list = []
    ###################### onnxruntime的模型信息
    ort_session = onnxruntime.InferenceSession(onnxFile)
    # 模型基本信息
    meta = ort_session.get_modelmeta()
    msg_list.append('modelMeta:')
    msg_list.append(f'    producer_name:{meta.producer_name}')
    msg_list.append(f'    graph_name:{meta.graph_name}')
    msg_list.append(f'    domain:{meta.domain}')
    msg_list.append(f'    description:{meta.description}')
    msg_list.append(f'    graph_description:{meta.graph_description}')
    msg_list.append(f'    version:{meta.version}')

    # 获取输入信息
    inputs = ort_session.get_inputs()
    msg_list.append(f'\n\nInput Node Name/Shape [{len(inputs)}]:')
    msg_list.extend(__fmt_node_arg(inputs))

    # 获取输出信息
    outputs = ort_session.get_outputs()
    msg_list.append(f'\n\nOutput Node Name/Shape [{len(outputs)}]:')
    msg_list.extend(__fmt_node_arg(outputs))

    # 获取重载初始化
    overinits = ort_session.get_overridable_initializers()
    msg_list.append(f'\n\nOverridableInitializer Node Name/Shape [{len(overinits)}]:')
    msg_list.extend(__fmt_node_arg(overinits))


    ###################### onnx 的模型信息
    try:
        model = onnx.load_model(onnxFile)
        graph = onnx.helper.printable_graph(model.graph)
        msg_list.append("\n\n" + graph)
    except Exception as e:
        print(e)
    ###################### 保存onnx模型信息
    with open(graphFile, 'w') as f:
        f.write('\n'.join(msg_list))

    if show_info:
        print(f'dump file... {onnxFile}')

    return graphFile