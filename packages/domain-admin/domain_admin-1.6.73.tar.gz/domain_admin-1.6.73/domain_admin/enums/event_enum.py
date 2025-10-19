# -*- coding: utf-8 -*-
"""
@File    : event_enum.py
@Date    : 2022-10-30
@Author  : Peng Shiyu
"""
from __future__ import print_function, unicode_literals, absolute_import, division


class EventEnum(object):
    """
    通知事件枚举值
    """
    # ssl证书到期 默认
    SSL_CERT_EXPIRE = 0

    # 域名到期
    DOMAIN_EXPIRE = 1

    # 监控异常
    MONITOR_EXCEPTION = 2

    # 托管证书到期
    SSL_CERT_FILE_EXPIRE = 3

    # 监控异常恢复
    MONITOR_EXCEPTION_RESTORE = 4
