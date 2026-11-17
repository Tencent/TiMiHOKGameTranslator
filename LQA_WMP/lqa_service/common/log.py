# -*- coding: utf-8 -*-
"""
# @file: log.py
# @time: 2021/11/1 14:28
# @desc:
"""
import os
import logging


def get_logger():
    _logger = logging.getLogger('handle')
    log_path = os.environ.get('LOG_PATH', './log')
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    _logger.setLevel(logging.INFO)
    fh = logging.FileHandler('{}/log_lqa.log'.format(log_path))
    fh.setFormatter(
        logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s %(funcName)s %(lineno)s - %(message)s"))
    _logger.addHandler(fh)
    return _logger


logger = get_logger()
