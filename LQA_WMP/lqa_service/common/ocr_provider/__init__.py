# -*- coding: utf-8 -*-
"""OCR 适配层入口

OCR 是**可选**能力，通过环境变量 ``OCR_PROVIDER`` 选择实现，默认 ``rapidocr``
（开源离线）。设为 ``none`` 或未安装任何引擎时，服务仍可正常启动与检测，
仅跳过依赖 OCR 的检测项。

用法::

    from common.ocr_provider import get_provider, is_available
    if is_available():
        data = get_provider().recognize(img_base64, project='demo')
"""
import logging
import time

from .base import OcrProvider, OcrError, NullOcr, quad_to_box

logger = logging.getLogger('handle')

#: provider 名称 -> (模块路径, 类名)
PROVIDERS = {
    'paddleocr': ('.paddle', 'PaddleOcrLocal'),
    'paddleocr_http': ('.paddle', 'PaddleOcrHttp'),
    'rapidocr': ('.local_engines', 'RapidOcr'),
    'easyocr': ('.local_engines', 'EasyOcr'),
    'tesseract': ('.local_engines', 'TesseractOcr'),
    'tencentcloud': ('.cloud', 'TencentCloudOcr'),
    'baidu': ('.cloud', 'BaiduOcr'),
    'azure': ('.cloud', 'AzureOcr'),
    'cvtest': ('.cvtest', 'CvtestOcr'),
    #: 显式关闭 OCR
    'none': ('.base', 'NullOcr'),
}

#: OCR_PROVIDER 取这些值时等同于 none
_DISABLED_ALIASES = ('', 'none', 'null', 'off', 'disabled', 'false')

_instance = None
_instance_key = None

#: 可用性探测缓存: (是否可用, 描述, 过期时间戳)
_probe_cache = None
#: 探测失败后的重试间隔（秒）；成功结果在进程内长期有效
_PROBE_RETRY_INTERVAL = 60
_PROBE_OK_TTL = 3600


def _build(name, config):
    if name not in PROVIDERS:
        raise OcrError(
            ' 未知的 OCR_PROVIDER=%s，可选: %s' % (name, ', '.join(sorted(PROVIDERS)))
        )
    import importlib

    module_path, class_name = PROVIDERS[name]
    module = importlib.import_module(module_path, package=__name__)
    return getattr(module, class_name)(config)


def resolve_name(name=None):
    """归一化 provider 名称：空值/关闭别名统一映射为 none"""
    if name is None:
        from config import baseconfig

        name = baseconfig.OCR_PROVIDER
    name = (name or '').strip().lower()
    if name in _DISABLED_ALIASES:
        return 'none'
    return name


def get_provider(name=None, config=None, cache=True):
    """获取 OCR provider 实例（默认按配置缓存，避免重复加载本地模型）

    未配置或配置为关闭时返回 :class:`NullOcr`，不会抛异常。
    """
    global _instance, _instance_key  # pylint: disable=global-statement

    from config import baseconfig

    name = resolve_name(name)
    if config is None:
        config = baseconfig.ocr_provider_config()
    if not cache:
        return _build(name, config)

    key = (name, tuple(sorted((k, str(v)) for k, v in config.items())))
    if _instance is None or _instance_key != key:
        _instance = _build(name, config)
        _instance_key = key
        logger.info('OCR provider 已初始化: %s', name)
    return _instance


def is_available(force=False):
    """OCR 能力是否可用（结果带缓存，可安全用于每次请求）

    :param force: True 时忽略缓存重新探测
    :return: (bool 是否可用, str 描述信息)
    """
    global _probe_cache  # pylint: disable=global-statement

    now = time.time()
    if not force and _probe_cache is not None and now < _probe_cache[2]:
        return _probe_cache[0], _probe_cache[1]

    name = resolve_name()
    if name == 'none':
        msg = '未配置 OCR（OCR_PROVIDER=none），依赖 OCR 的检测项将跳过'
        _probe_cache = (False, msg, now + _PROBE_OK_TTL)
        return False, msg

    try:
        provider = get_provider()
        if not getattr(provider, 'capable', True):
            msg = 'OCR 已关闭: %s' % name
            _probe_cache = (False, msg, now + _PROBE_OK_TTL)
            return False, msg
        detail = provider.test_connection()
        msg = '%s: %s' % (name, detail)
        _probe_cache = (True, msg, now + _PROBE_OK_TTL)
        logger.info('OCR 可用 - %s', msg)
        return True, msg
    except OcrError as ex:
        msg = 'OCR 不可用(%s): %s' % (name, ex)
    except Exception as ex:  # pylint: disable=broad-except
        msg = 'OCR 探测异常(%s): %s' % (name, ex)
    _probe_cache = (False, msg, now + _PROBE_RETRY_INTERVAL)
    logger.warning('%s；将跳过依赖 OCR 的检测项', msg)
    return False, msg


def reset_cache():
    """清空 provider 与探测缓存（测试用）"""
    global _instance, _instance_key, _probe_cache  # pylint: disable=global-statement
    _instance = None
    _instance_key = None
    _probe_cache = None
