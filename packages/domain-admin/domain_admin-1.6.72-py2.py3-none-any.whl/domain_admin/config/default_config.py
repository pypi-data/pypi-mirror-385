# -*- coding: utf-8 -*-
"""
@File    : default_config.py
@Date    : 2023-06-13
"""
from __future__ import print_function, unicode_literals, absolute_import, division

from domain_admin.utils import secret_util, md5_util
from domain_admin.version import VERSION

# 管理员默认的 账号，用户名
DEFAULT_ADMIN_USERNAME = 'admin'
DEFAULT_ADMIN_PASSWORD = '123456'

# header请求头中携带 token 参数名称
TOKEN_KEY = 'X-Token'

# header请求头中携带 language 参数名称
LANGUAGE_KEY = 'X-Language'

# 默认的token有效时长 单位：天
DEFAULT_TOKEN_EXPIRE_DAYS = 7

# 默认的过期提醒时间 单位：天
DEFAULT_BEFORE_EXPIRE_DAYS = 3

# 默认续期时间 单位：天
DEFAULT_RENEW_DAYS = 30

# secret_key
DEFAULT_SECRET_KEY = secret_util.get_random_secret()

# prometheus_key
DEFAULT_PROMETHEUS_KEY = md5_util.md5(DEFAULT_SECRET_KEY)

# 默认数据库链接
DEFAULT_DB_CONNECT_URL = "sqlite:///database/database.db"

# 默认的ssh连接端口
DEFAULT_SSH_PORT = 22

# 项目主页地址
PROJECT_HOME_URL = 'https://github.com/mouday/domain-admin'

# user agent
USER_AGENT = "Mozilla/5.0 (compatible; DomainAdmin/{version}; +{url})".format(
    version=VERSION,
    url=PROJECT_HOME_URL,
)
