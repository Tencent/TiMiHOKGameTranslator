# -*- coding: utf-8 -*-
"""OCR provider 自检工具

用法::

    python tests/check_ocr.py              # 检测当前 OCR_PROVIDER 配置
    python tests/check_ocr.py paddleocr    # 指定 provider
    python tests/check_ocr.py --list       # 列出全部可选 provider
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.ocr_provider import PROVIDERS, get_provider, OcrError  # noqa: E402


def main():
    args = sys.argv[1:]
    if args and args[0] in ('--list', '-l'):
        print('可选 OCR_PROVIDER:')
        for name in sorted(PROVIDERS):
            print('  -', name)
        return 0

    name = args[0] if args else None
    try:
        provider = get_provider(name=name, cache=False)
    except OcrError as err:
        print('[FAIL] 初始化失败: %s' % err)
        return 1

    print('provider = %s (远程服务: %s)' % (provider.name, provider.remote))
    if not getattr(provider, 'capable', True):
        print('[SKIP] %s' % provider.test_connection())
        print('       OCR 为可选能力，当前不影响服务启动；'
              '仅「错译」与「文本超文本框」检测会被跳过。')
        return 0
    try:
        print('[OK]', provider.test_connection())
        return 0
    except OcrError as err:
        print('[FAIL] %s' % err)
        print('       OCR 为可选能力：服务仍可启动，但「错译」与'
              '「文本超文本框」检测将被跳过。')
        return 1
    except Exception as err:  # pylint: disable=broad-except
        print('[FAIL] %s: %s' % (type(err).__name__, err))
        return 1


if __name__ == '__main__':
    sys.exit(main())
