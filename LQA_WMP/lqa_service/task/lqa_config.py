# -*- coding: utf-8 -*-
"""
# @file: lqa_config.py
# @time: 2022/6/26
# @desc: lqa本地化支持测试类型相关配置
"""
from enum import Enum


class LqaCheckType(Enum):
    NO_TRANS = 1  # 漏译
    OVER_FRAME = 2  # 超框
    NO_KEY = 3  # 漏key
    OVERLAP = 4  # 文本框重叠
    ERROR_TRANS = 5  # 错译
    NON_PROBLEM = 6  # non_problem自定义
    NON_RECTANGLE = 7  # 非标准框


class LqaCheckSubType(Enum):
    OVER_FRAME_TEXT_TEXT = 0  # 文本超文本框
    OVER_FRAME_TEXT_IMAGE = 1  # 文本超图像框


# 结果标记样式
class DrawStyle(Enum):
    GT_IMG = ((255, 255, 255), 2)
    GT_TEXT = ((0, 0, 255), 2)
    OCR = ((0, 255, 0), 1)
    NO_TRANS = ((0, 140, 255), 4)
    OVER_FRAME = ((0, 0, 255), 2)
    NO_KEY = ((0, 255, 255), 3)
    OVERLAP = ((255, 0, 255), 1)
    ERROR_TRANS = ((255, 255, 0), 5)
    NON_PROBLEM = ((255, 0, 0), 4)
    NON_RECTANGLE = ((255, 0, 255), 2)
    PRE_ERR = ((255, 0, 255), 5)


class Language(Enum):
    zh_CN = 0  # 简体中文
    zh_TW = 1  # 繁体中文 (台湾)
    en = 2  # 英文
    ja_JP = 3  # 日文
    th = 4  # 泰文
    vn = 5  # 越南


if __name__ == '__main__':
    pass
