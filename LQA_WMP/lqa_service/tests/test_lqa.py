# -*- coding: utf-8 -*-
"""
# @file: test_lqa.py
# @time: 2022/4/27 11:48
# @desc: lqa本地化文本异常检测服务测试接口
"""
import json
import time
import base64
import unittest
import requests
import cv2
from common.tools import base64_to_mat


import os

# 服务地址与测试数据路径均可通过环境变量覆盖：
#   LQA_TEST_HOST / LQA_TEST_PORT / LQA_TEST_DATA_DIR
DEFAULT_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test', '0')


class LqaTestCase(unittest.TestCase):
    host = os.getenv("LQA_TEST_HOST", "127.0.0.1")
    port = int(os.getenv("LQA_TEST_PORT", "8086"))

    def setUp(self):
        data_dir = os.getenv("LQA_TEST_DATA_DIR", DEFAULT_DATA_DIR)
        img_path = os.path.join(data_dir, "screenShot.png")
        self.fd = open(img_path, "rb")
        self.img_base64 = base64.b64encode(self.fd.read()).decode("ascii")
        self.load_f = open(os.path.join(data_dir, "v3_result.json"), 'rb')
        self.rect_locations = json.load(self.load_f)
        self.supervised = None
        self.language = None
        self.check_type = None  # 默认全部异常类型
        # 差异识别的历史图，未配置时不启用
        history_img_path = os.getenv("LQA_TEST_HISTORY_IMG", "")
        self.history_fd = None
        self.history_img_base64 = None
        if history_img_path and os.path.exists(history_img_path):
            self.history_fd = open(history_img_path, "rb")
            self.history_img_base64 = base64.b64encode(self.history_fd.read()).decode("ascii")
        self.history_result = {}

    def test_lqa(self):
        st = time.time()
        path = "/image/lqa_check/"
        body = {
            "img_base64": self.img_base64,
            "rect_locations": self.rect_locations,
            "language": self.language,
            "supervised": self.supervised,
            "check_type": self.check_type,
            "history_img_base64": self.history_img_base64,
            "history_result": self.history_result,
        }
        url = f"http://{self.host}:{self.port}{path}"
        print(url)
        headers = {"project-method": f"{os.getenv('LQA_TEST_PROJECT', 'lqa')}_lqa"}
        res = requests.post(url, json=body, headers=headers)
        if res.status_code == 200:
            res_dict = res.json()
            if res_dict["success"]:
                result = res_dict["result"]
                mark_img = base64_to_mat(result["mark_img"])
                rect_img = base64_to_mat(result["rect_img"])
                print(result["check_detail"])
                print('耗时', time.time() - st)
                if mark_img is not None:
                    cv2.namedWindow("mark_img", cv2.WINDOW_NORMAL)
                    cv2.imshow("mark_img", mark_img)
                    cv2.imwrite("lqa_mark_img.png", mark_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                if rect_img is not None:
                    cv2.namedWindow("rect_img", cv2.WINDOW_NORMAL)
                    cv2.imshow("rect_img", rect_img)
                    cv2.imwrite("lqa_rect_img.png", rect_img, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                cv2.waitKey()
            else:
                print(res_dict["err_msg"])
        else:
            print(res.status_code)

    def tearDown(self):
        self.fd.close()
        self.load_f.close()
        if self.history_fd:
            self.history_fd.close()
        print("test end")


if __name__ == '__main__':
    unittest.main()
