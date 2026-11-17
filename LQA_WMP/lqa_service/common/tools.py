# -*- coding: utf-8 -*-
"""
# @file: tools.py
# @time: 2022/4/26 18:11
# @desc: 一些数据处理的通用接口
"""
import base64
import cv2
import numpy as np


def base64_to_mat(base64_img, gray=False, alpha=False):
    """ 数据base64转ndarray
    :param base64_img: str, base64格式的图像数据
    :param gray: bool, 标记是否是灰度图
    :param alpha: bool, 标记数据是否带有alpha通道
    :return: ndarray格式的图像数据
    """
    if base64_img is None:
        return None
    img_b64decode = base64.b64decode(base64_img)
    # np.fromstring 的二进制模式在 numpy>=1.22 已废弃、2.x 中移除，改用 frombuffer
    img_array = np.frombuffer(img_b64decode, np.uint8)
    if gray:
        trans_type = cv2.IMREAD_GRAYSCALE
    elif alpha:
        trans_type = -1
    else:
        trans_type = cv2.COLOR_BGR2RGB
    img = cv2.imdecode(img_array, trans_type)
    return img


def mat_to_base64(img):
    """ 数据ndarray转base64
    :param img: ndarray, ndarray格式的图像数据
    :return: base64格式的图像数据
    """
    if img is None:
        return None
    # ndarray.tostring() 在 numpy 2.x 中已移除，改用等价的 tobytes()
    image = cv2.imencode('.jpg', img)[1].tobytes()
    base64_img = base64.b64encode(image).decode()
    return base64_img


def img_draw_rect(img, rect, draw_style=((0, 0, 255), 1)):
    """标记图像
    :param img: ndarray, 图像
    :param rect: x1, y1, x2, y2, 标记位置(标准矩形框)， 非标框4个点8维向量
    :param draw_style: tuple, 绘制样式, 取值DrawStyle,包括颜色, 线条size
    :return: img, 标记后的图像
    """
    if rect:
        if len(rect) == 4:
            x1, y1, x2, y2 = rect
            cv2.rectangle(img, (x1, y1), (x2, y2), draw_style[0], draw_style[1])

        if len(rect) == 8:
            rect_array = np.array(rect)
            rect_reshape = rect_array.reshape(-1, 2, 1)
            cv2.polylines(img, [rect_reshape], isClosed=True, color=draw_style[0], thickness=draw_style[1])  # 红色多边形

    return img
