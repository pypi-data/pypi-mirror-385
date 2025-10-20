#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2020/6/4 18:13:09

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import inspect, contextlib, types, sys
#===============================================================================
# 
#===============================================================================

__all__ = ['dump', 'dump_help', 'is_method_overide', 'get_members', 'get_module_path']

_MODULE_DEFAULT_FIELDS = ['__builtins__', '__cached__', '__doc__', '__file__',
                          '__loader__', '__name__', '__package__', '__path__', '__spec__']

_CLASS_DEFAULT_FIELDS = ['__dict__', '__doc__', '__module__', '__weakref__',
                         '__init_subclass__', '__subclasshook__', '__class__']

def get_module_path(mod):
    pth = ''

    fname = getattr(mod, '__file__', '')
    if fname:
        pth = fname

    nsPath = getattr(mod, '__path__', None)
    if nsPath:
        pth = nsPath[0]
    return pth

def _is_third_pkg(mod):
    return 'site-packages' in get_module_path(mod)

def _is_in_same_pkg(mod1, mod2):
    mod1 = get_module_path(mod1)
    mod2 = get_module_path(mod2)
    return mod1 in mod2

def is_method_overide(obj, method_name, parent=None):
    '''判断方法是否覆盖父类的方法'''
    if parent is None:
        parent = object

    mth = getattr(obj, method_name)
    if hasattr(parent, method_name):
        p_mth_id = id(getattr(parent, method_name))
        if isinstance(obj, type):  # 如果是类
            if id(mth) == p_mth_id:
                return True
        else:  # 如果是对象
            if id(getattr(obj.__class__, method_name)) == p_mth_id:
                return True
    return False

def dump_help(obj):
    with open('help-%s.txt' % _val_name(obj), 'w') as f, \
            contextlib.redirect_stdout(f):
        help(obj)

def dump(obj, ignore_fields = tuple(),
                use_all = True,
                dump_format = None,
                skip_moudle_defaults = True,
                skip_class_defaults=True,
                skip_underscore=True,
                stream=None):

    # # 空对象,直接不处理
    # if cfg is None:
    #     print('None')
    #     return

    all_ModuleType = [] #模块
    all_Class = []      #类
    all_Attr = []       #属性
    all_Funcs = []      #函数
    if stream is None:
        stream = sys.stdout
    name_value_iter = get_members(obj, ignore_fields=ignore_fields,
                                  use_all=use_all, skip_moudle_defaults=skip_moudle_defaults,
                                  skip_class_defaults=skip_class_defaults,
                                  skip_underscore=skip_underscore)
    stream.write(f'\n########## {type(obj)} ##########\n')
    if dump_format is not None:
        stream.write(f'from {obj.__name__} import *\n')

    for item in name_value_iter:
        k, v = item
        if isinstance(v, type): # class类型
            all_Class.append(item)

        elif isinstance(v, types.ModuleType): # 模块类型
            if not _is_third_pkg(v): # 保证是第三方库
                continue
            if isinstance(obj, types.ModuleType): #保证在同一个包里面
                if not _is_in_same_pkg(obj, v):
                    continue
            all_ModuleType.append(item)

        elif isinstance(v, (types.FunctionType,types.MethodType,types.WrapperDescriptorType,
                            types.MethodWrapperType, types.MethodDescriptorType, types.BuiltinFunctionType,
                            types.BuiltinMethodType) #可执行的函数类型
                        ):
            all_Funcs.append(item)
        else:
            all_Attr.append(item)

    if all_ModuleType:
        stream.write('##### module\n')
        for k,v in all_ModuleType:
            if dump_format is None:
                stream.write('  # %s[%s]\n' % (k, _val_doc(v)))
            else:
                stream.write('  %s #[%s]\n' % (k, _val_doc(v)))

    if all_Class:
        stream.write('##### class\n')
        for k,v in all_Class:
            if dump_format is None:
                stream.write('  # %s[%s]\n' % (k, _val_doc(v)))
            else:
                stream.write('  %s #[%s]\n' % (k, _val_doc(v)))

    if all_Attr:
        stream.write('##### attr\n')
        for k,v in all_Attr:
            if dump_format is None or (k.startswith('__') and k.endswith('__')):
                stream.write('  # %s[%s] [%s]\n' % (k, _val_str(v), _val_doc(v)))
            else:
                stream.write('  %s #[%s] [%s]\n' % (k, _val_str(v), _val_doc(v)))

    if all_Funcs:
        stream.write('##### func\n')
        for k,v in all_Funcs:
            if dump_format is None:
                stream.write('  # %s%s [%s]\n' % (k, _func_signature(v), _val_doc(v)))
            else:
                stream.write('  %s #%s [%s]\n' % (k, _func_signature(v), _val_doc(v)))
    stream.write("\n")

def _val_str(v):
    try:
        return str(v).replace('\n', ' ').replace('\r', ' ')[0:100]
    except Exception as e:
        return ""
def _val_doc(v):
    if isinstance(v, str):
        return  '`str`'
    if isinstance(v, bytes):
        return  '`bytes`'
    elif isinstance(v, int):
        return  '`integer`'
    elif isinstance(v, dict):
        return  '`dict`'
    elif isinstance(v, set):
        return  '`set`'
    elif isinstance(v, frozenset):
        return '`fronzenset`'
    elif isinstance(v, float):
        return '`float`'
    elif isinstance(v, tuple):
        return '`tuple`'
    elif isinstance(v, list):
        return '`list`'

    try:
        import re
        doc = inspect.getdoc(v)
        doc = re.sub(' +', ' ', doc)
        return doc.replace('\n', ' ').replace('\r', ' ')[0:250]
    except Exception as e:
        return  ''

def _val_name(v):
    try:
        name = v.__name__
    except Exception:
        try:
            name = v.__class__.__name__
        except Exception:
            name = 'none'
    return name

def _func_signature(v):
    try:
        return str(inspect.signature(v))
    except: # 有些函数没有签名
        return "(...)"

def get_members(obj,
                ignore_fields = tuple(),
                use_all = True,
                skip_moudle_defaults = True,
                skip_class_defaults=True,
                skip_underscore=True):
    '''
    获取可能的属性列表
    '''

    # 默认从 __all__获取属性
    datalist = []
    if use_all:
        for k in getattr(obj, '__all__', tuple()):
            if hasattr(obj, k):
                datalist.append( (k, getattr(obj, k)) )

    # 获取所有属性
    if not datalist: # 如果 __all__是空的,就从模块里获取
        datalist = _getmembers(obj)

    if isinstance(ignore_fields, str):
        ignore_fields = ignore_fields.split()

    datalist.sort(key=lambda kv: kv[0])

    # 把 __init__放在最前面
    for i,(k,v) in enumerate(datalist):
        if k == '__init__':
            del datalist[i]
            datalist.insert(0, (k, v))
            break

    #字段过滤
    for k,v in datalist:

        # 忽略的字段
        if k in ignore_fields:
            continue

        # 私有变量不访问
        if skip_underscore and k.startswith('_') :
            if not k.startswith('__') or not k.endswith('__'):
                continue

        # 跳过模块中方法
        if skip_moudle_defaults and isinstance(obj, types.ModuleType):
            if k in _MODULE_DEFAULT_FIELDS:
                continue

        if skip_class_defaults and hasattr(obj, '__class__'):

            # 跳过默认的参数
            if k in _CLASS_DEFAULT_FIELDS:
                continue

            # 跳过 object 中没有覆盖的方法
            if is_method_overide(obj, k):
                continue

        yield k,v

    return datalist

def _getmembers(object, predicate=None):

    if inspect.isclass(object):
        mro = (object,) + inspect.getmro(object)
    else:
        mro = ()

    results = []
    processed = set()
    names = dir(object)

    try:
        for base in object.__bases__:
            for k, v in base.__dict__.items():
                if isinstance(v, types.DynamicClassAttribute):
                    names.append(k)
    except AttributeError:
        pass

    for key in names:
        try:
            value = getattr(object, key)
            if key in processed:
                raise AttributeError
        except AttributeError:
            for base in mro:
                if key in base.__dict__:
                    value = base.__dict__[key]
                    break
            else:
                continue
        except Exception:
            continue

        if not predicate or predicate(value):
            results.append((key, value))
        processed.add(key)

    return results
