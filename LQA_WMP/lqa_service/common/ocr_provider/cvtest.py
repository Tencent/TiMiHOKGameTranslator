# -*- coding: utf-8 -*-
"""CVTest OCR 适配（内网自建服务，向后兼容）

协议::

    POST {OCR_URL}
    headers: {"project-method": "<project>_ocr"}   # 缺失会被判为 No authorization
    body:    {"img_base64": "...", "location": null, "projectid": 19998}
    resp:    {"errCode": 0, "data": [{"area": [x1,y1,x2,y2], "result": "文本"}]}
"""
import time
import logging

import requests

from .base import OcrProvider, OcrError

logger = logging.getLogger('handle')

MAX_RETRY = 10
RETRY_INTERVAL = 0.6


class CvtestOcr(OcrProvider):
    """内网 CVTest OCR 服务"""

    name = 'cvtest'
    remote = True

    def recognize(self, img_base64, project=None):
        url = self.config.get('url')
        if not url:
            raise OcrError('未配置 OCR_URL')
        timeout = int(self.config.get('timeout', 60))
        project_id = int(self.config.get('project_id', 19998))

        data = {'img_base64': img_base64, 'location': None, 'projectid': project_id}
        headers = {}
        # 该服务依赖 project-method 请求头鉴权，缺失时返回 No authorization 且 data 为 null
        project = project or self.config.get('default_project')
        if project:
            headers['project-method'] = '%s_ocr' % project

        last_err = None
        for attempt in range(MAX_RETRY):
            try:
                resp = requests.post(url=url, json=data, headers=headers, timeout=timeout)
            except requests.RequestException as err:
                raise OcrError('OCR 服务请求失败: %s' % err) from err
            if resp.status_code != 200:
                raise OcrError('OCR 服务返回 HTTP %s' % resp.status_code)
            try:
                payload = resp.json()
            except ValueError as err:
                raise OcrError('OCR 服务返回非 JSON') from err

            err_code = payload.get('errCode')
            if err_code == 0:
                result = payload.get('data')
                if result is None:
                    # errCode=0 但 data 为空，通常是鉴权失败，历史实现会静默返回 None
                    raise OcrError(
                        'OCR 服务未返回数据: %s（请确认请求头 project-method 及项目授权）'
                        % (payload.get('err_msg') or payload.get('errMsg') or '未知原因')
                    )
                return result
            if err_code == -2:  # 服务侧繁忙，可重试
                last_err = payload.get('errMsg')
                logger.warning('OCR 重试 %s/%s: %s', attempt + 1, MAX_RETRY, last_err)
                time.sleep(RETRY_INTERVAL)
                continue
            raise OcrError('OCR 服务错误 errCode=%s %s' % (err_code, payload.get('errMsg')))
        raise OcrError('OCR 服务重试 %s 次仍失败: %s' % (MAX_RETRY, last_err))
