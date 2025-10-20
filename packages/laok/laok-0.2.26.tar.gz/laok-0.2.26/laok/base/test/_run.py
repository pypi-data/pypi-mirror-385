#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2020/6/4 17:25:47

@author: LiuKuan
@copyright: Apache License, Version 2.0
'''
import inspect, sys, time, traceback, math, re, codecs
from datetime import datetime
#===============================================================================
# 交互式运行
#===============================================================================
PRINT_FUNC_COUNT = 3

__all__ = ['run', 'main_module']
main_module = sys.modules.get('__main__')

# 执行计时
def _time_run(_kvfunc, _repeat = 1, **kws):
    name, func = _kvfunc
    print('{}==begin[date:{}]'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

    t0 = time.time()
    for i in range(_repeat):
        try:
            func(**kws)
        except (SystemExit, KeyboardInterrupt):
            break
        except Exception as e:
            print ( '\nexception in call function---->\n%s' % traceback.format_exc() )
            break
    elapse = time.time() - t0
    print ( '{}==end[use time:{}s]\n'.format(name, elapse) )

#从文件提取特定函数名字,主要是用于排序
def _find_order_names(filename, re_pat):
    with codecs.open(filename, encoding='utf8') as f:
        for i,line in enumerate(f, 1):
            res = re_pat.match(line)
            if res:
                yield i,res.group(1)

# 删除头尾
def _trim(name, _suffix):
    if name.startswith(_suffix):
        name = name[len(_suffix):]
    if name.endswith(_suffix):
        name = name[:-len(_suffix)]
    return name

def run(_opt='last', _suffix ='_lk', _module = None, _repeat = 1, **kws):
    '''执行以 _suffix 结尾的函数
    :param _opt: last/first/select/all/function_name
    :return:
    '''
    RE_PAT = re.compile(r"^def\s*(.*?{pat})|({pat}.*?)\(.*?\):.*".format(pat = _suffix))

    # 获取所有 _suffix 结尾的函数
    if _module is None:
        _module = main_module
    kvList = [(_trim(k, _suffix), v)
              for k,v in inspect.getmembers(_module, inspect.isfunction)
              if k.endswith(_suffix)]

    # 检测是否有测试用例
    if not kvList:
        return

    # 按照代码文本顺序排序
    _kvOrder = {}
    for order, name in  _find_order_names(_module.__file__, RE_PAT):
        _kvOrder[_trim(name, _suffix)] = order
    kvList.sort(key = lambda pair: _kvOrder[pair[0]])

    # 根据选择,执行函数
    if _opt == 'first':
        return _time_run(kvList[0], _repeat, **kws)
    elif _opt == 'last':
        return _time_run(kvList[-1], _repeat,**kws)
    elif _opt == 'all':
        for kv in kvList:
            _time_run(kv, _repeat, **kws)
    elif _opt in ['select','']:
        _len = len(kvList)
        idx_w = math.ceil(math.log10(_len))  #索引的宽度
        idx_name_w = {} #名字列的宽度
        for i, (k,_) in enumerate(kvList):
            _kw = len(k)
            i = i % PRINT_FUNC_COUNT
            if i in idx_name_w:
                idx_name_w[i] = max( _kw, idx_name_w[i] )
            else:
                idx_name_w[i] = _kw

        while True: # 循环执行任务
            for i, (k,_) in enumerate(kvList):
                fmt = "<%0{}s>%-{}s".format(idx_w, idx_name_w[ i % PRINT_FUNC_COUNT])
                # print(fmt, end=' ')
                print( fmt % (i, k), end=" ")
                if (i+1) % PRINT_FUNC_COUNT == 0:
                    print()
            if (i+1) % PRINT_FUNC_COUNT != 0:
                print()

            try:
                i = input('which func do you want to run , -1=quit , -2=run-all:')
                i = int(i) # 输入索引
            except:
                i = _len - 1 #执行最后一个

            if i == -2: #运行所有的task,退出
                for kv in kvList:
                    _time_run(kv, _repeat, **kws)
                return
            elif i == -1: #直接退出
                return
            else: #执行选择的任务
                i = (i + _len) % _len
                _time_run( kvList[i], _repeat,**kws)

            if _opt == '': #执行一次,则退出
                return
    else : #否则判断是否执行任务列表
        if not isinstance(_opt, (list,tuple) ):
            run_list = (_opt, )
        else:
            run_list = _opt

        for _run_op in run_list:
            for kv in kvList:
                if (isinstance(_run_op, str) and kv[0] == _trim(_run_op, _suffix) ) \
                        or (inspect.isfunction(_run_op) and kv[1] == _run_op):
                    _time_run(kv, _repeat,**kws)
