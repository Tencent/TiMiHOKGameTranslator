# -*- coding: utf-8 -*-
"""OCR 适配层：抽象接口

LQA 的超框/漏译检测依赖 OCR 返回 **文本内容 + 精确边界框**，
因此只接受能同时给出两者的 OCR 服务。

统一返回格式（与历史接口保持一致）：
    [{"area": [x1, y1, x2, y2], "result": "识别出的文本"}, ...]
"""
from abc import ABC, abstractmethod
import base64
import logging

import numpy as np
import cv2

logger = logging.getLogger('handle')


class OcrError(Exception):
    """OCR 调用失败"""


def base64_to_ndarray(img_base64):
    """base64 -> BGR ndarray"""
    raw = base64.b64decode(img_base64)
    img = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise OcrError('图像解码失败')
    return img


def quad_to_box(points):
    """任意多边形顶点 -> 轴对齐包围盒 [x1, y1, x2, y2]

    PaddleOCR / EasyOCR 等返回的是四点多边形，需转为 LQA 需要的矩形。
    """
    xs = [int(round(float(p[0]))) for p in points]
    ys = [int(round(float(p[1]))) for p in points]
    return [min(xs), min(ys), max(xs), max(ys)]


class OcrProvider(ABC):
    """OCR 提供方抽象基类"""

    name = 'base'
    #: 是否依赖外部网络服务
    remote = True
    #: 是否提供真实 OCR 能力（NullOcr 为 False）
    capable = True

    def __init__(self, config=None):
        self.config = config or {}

    @abstractmethod
    def recognize(self, img_base64, project=None):
        """识别整图文字

        :param img_base64: str, base64 编码的图像
        :param project: str, 调用方项目标识（部分服务用于鉴权/路由，可忽略）
        :return: list[dict], [{"area": [x1,y1,x2,y2], "result": "文本"}, ...]
        :raises OcrError: 调用失败
        """

    def test_connection(self):
        """连通性自检，返回描述信息字符串"""
        img = np.full((48, 160, 3), 255, np.uint8)
        cv2.putText(img, 'LQA123', (6, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 2)
        ok, buf = cv2.imencode('.png', img)
        if not ok:
            raise OcrError('测试图编码失败')
        data = self.recognize(base64.b64encode(buf).decode('ascii'))
        texts = [d.get('result', '') for d in (data or [])]
        return '连接正常，识别到 %d 个文本块: %s' % (len(texts), texts[:5])


class NullOcr(OcrProvider):
    """空实现：显式声明「不使用 OCR」（OCR_PROVIDER=none）

    OCR 在本服务中是可选能力。选用本 provider 时不会产生任何识别调用，
    依赖 OCR 的检测项（错译、文本超框）自动跳过，其余检测照常进行。
    """

    name = 'none'
    remote = False
    capable = False

    def recognize(self, img_base64, project=None):
        return []

    def test_connection(self):
        return '已显式关闭 OCR（OCR_PROVIDER=none），依赖 OCR 的检测项将跳过'
