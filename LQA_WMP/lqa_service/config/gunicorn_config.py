# -*- coding: utf-8 -*-
"""
# @file: gunicorn_config.py
# @time: 2021/9/21 16:41
# @desc:
"""
import os

bind = os.getenv("BIND", '0.0.0.0:8086')
worker_class = os.getenv("WORK_CLASS", "gevent")
# 注意：此处历史上误用了 BIND 变量，设置 BIND 后会导致 int() 解析失败
timeout = int(os.getenv("TIMEOUT", 120))

# os.cpu_count()
workers = int(os.getenv("GUNICORN_WORKERS", 3))
accesslog = os.getenv("ACCESSLOG", "gunicirn_access.log")
errorlog = os.getenv("ERRORLOG", "gunicirn_error.log")
loglevel = os.getenv("LOGLEVEL", "info")
