# -*- coding: utf-8 -*-
"""
token_service.py
"""
from __future__ import print_function, unicode_literals, absolute_import, division
from datetime import datetime, timedelta

import jwt
from flask import current_app

from domain_admin.config import SECRET_KEY, TOKEN_EXPIRE_DAYS
from domain_admin.enums.config_key_enum import ConfigKeyEnum
from domain_admin.utils.flask_ext.app_exception import ForbiddenAppException, AppException


def encode_token(payload):
    """
    获取token
    :param payload: dict
    :return: byte
    """
    # config = system_service.get_system_config()
    # secret_key = config['secret_key']

    secret_key = current_app.config[ConfigKeyEnum.SECRET_KEY]
    token_expire_days = int(current_app.config[ConfigKeyEnum.TOKEN_EXPIRE_DAYS])

    # bugfix 用户删除token过期天数变量后报错
    # token_expire_days = TOKEN_EXPIRE_DAYS

    # 使用utc时间
    payload['exp'] = datetime.utcnow() + timedelta(days=token_expire_days)

    # 返回 str 部分Python版本会报错
    return jwt.encode(payload=payload, key=secret_key, algorithm='HS256')


def decode_token(token):
    """
    验证并解析token
    :param token: str
    :return:  dict
    """
    # config = system_service.get_system_config()

    secret_key = current_app.config[ConfigKeyEnum.SECRET_KEY]

    try:
        return jwt.decode(jwt=token, key=secret_key, algorithms=['HS256'])
    except Exception:
        raise AppException('token无效')


if __name__ == '__main__':
    data = {'name': 'Tom'}
    w = encode_token(data)
    print(w)

    print(decode_token(w))
