# -*- coding: utf-8 -*-
"""
# @file: test_image_extraction_local.py
# @time: 2022/7/27
# @desc: 图像前景提取本地测试接口 (支持批量测试)
"""
import base64
import os
import cv2
from task.image_processing import ImageProcessing


def batch_test(data_dir, zero_type, position_type):
    """批量测试图像前景提取
    :param data_dir: str, 测试数据目录
    :param zero_type: int, 原点位置类型
    :param position_type: int, 位置表示方式类型
    :return: dict, 测试结果
    """
    img_base64_batch = {}
    for path, _, files in os.walk(data_dir):
        for file in files:
            print('当前检测: ', path, file)
            if file.endswith('.png'):
                img_path = os.path.join(path, file)
                f = open(img_path, "rb")
                img_base64 = base64.b64encode(f.read()).decode("ascii")
                if img_base64:
                    img_base64_batch[file] = img_base64
    res = ImageProcessing.image_extraction(img_base64_batch, zero_type=zero_type, position_type=position_type)
    return res


def save_res(data_dir, res_data, zero_type, position_type, show_img=False, save_img=False, save_dir=None):
    """图像前景提取结果保存
    :param data_dir: str, 测试数据目录
    :param res_data: dict, 测试结果数据
    :param zero_type: int, 原点位置类型
    :param position_type: int, 位置表示方式类型
    :param show_img: bool, 是否本地显示结果图像
    :param save_img: bool, 是否保存结果图像
    :param save_dir: str, 结果图像保存目录
    :return:
    """
    for item in res_data:
        img_path = os.path.join(data_dir, item)
        img = cv2.imread(img_path, flags=-1)
        h, w = img.shape[:2]
        x1, y1, x2, y2 = res_data[item]
        if position_type == 1:
            x1 = int(x1 * w)
            y1 = int(y1 * h)
            x2 = int(x2 * w)
            y2 = int(y2 * h)
        if zero_type == 1:
            y1 = h - y1
            y2 = h - y2
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0, 255), 1)
        if show_img:
            cv2.imshow(item, img)
        if save_img and save_dir:
            save_path = os.path.join(save_dir, item)
            cv2.imwrite(save_path, img)
    if show_img:
        cv2.waitKey(0)


def test(data_dir, zero_type, position_type, show_img=False, save_img=False, save_dir=None):
    """ 测试入口
    :param data_dir: str, 测试数据目录
    :param zero_type: int, 原点位置类型
    :param position_type: int, 位置表示方式类型
    :param show_img: bool, 是否本地显示结果图像
    :param save_img: bool, 是否保存结果图像
    :param save_dir: str, 结果图像保存目录
    :return:
    """
    res = batch_test(data_dir, zero_type=zero_type, position_type=position_type)
    print('结果:', res)
    res_data = res['image_extraction']
    save_res(data_dir, res_data, zero_type, position_type, show_img=show_img, save_img=save_img, save_dir=save_dir)


if __name__ == '__main__':
    # 可通过 LQA_TEST_DATA_DIR / LQA_TEST_SAVE_DIR 指定目录
    _base = os.path.dirname(os.path.abspath(__file__))
    _data_dir = os.getenv('LQA_TEST_DATA_DIR', os.path.join(_base, 'test'))
    _save_dir = os.getenv('LQA_TEST_SAVE_DIR', os.path.join(_base, 'test', 'result'))
    test(_data_dir, 0, 0, show_img=False, save_img=True, save_dir=_save_dir)
