# -*- coding: utf-8 -*-
"""
# @file: util_network.py
# @time: 2022/1/7 11:14
# @desc:
"""
from flask import jsonify


def response(success=True, err_msg="", result=None, **args):
    """ 网络请求response消息处理
    :param success: bool,  http相应码
    :param err_msg: str, 错误消息
    :param result: 结果数据
    :param args: dict,其他补充内容
    :return: response数据
    """
    ret = {
        "success": success,
        "err_msg": err_msg,
        "result": result
    }
    ret.update(args)
    return jsonify(ret)
