# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import, division
from flask import request, g

from domain_admin.config import ADMIN_USERNAME, TOKEN_KEY
from domain_admin.log import logger
from domain_admin.model.user_model import UserModel
from domain_admin.service import token_service
from domain_admin.utils.flask_ext.app_exception import UnauthorizedAppException, ForbiddenAppException

# 白名单
WHITE_LIST = [
    '/api/login',
    # 暂时不开放注册，安全起见先关闭
    '/api/register',
    '/api/getSystemVersion',
]

# 仅管理账号可访问的接口
ADMIN_API_LIST = [
    # 全局配置管理
    # '/api/getAllSystemConfig',
    # '/api/updateSystemConfig',
    # '/api/getSystemEnvConfig',
    # '/api/getCronConfig',
    # '/api/updateCronConfig',

    # 用户管理
    # '/api/getUserList',
    # '/api/addUser',
    # '/api/updateUserStatus',
    # '/api/deleteUser'
    # '/api/resetUserPasswordUser'
]

API_PREFIX = '/api'


def parse_token():
    logger.info('check_permission: %s', request.path)

    # 仅校验api
    if not request.path.startswith(API_PREFIX):
        return

    # 白名单直接通过
    if request.path in WHITE_LIST:
        return

    # 获取token
    token = request.headers.get(TOKEN_KEY)

    if token:
        # 解析token，并全局挂载
        payload = token_service.decode_token(token)
        g.user_id = payload['user_id']

    # root 权限 api
    # if request.path in ADMIN_API_LIST:
    #     user_row = UserModel.get_by_id(g.user_id)
    #
    #     if user_row.username != ADMIN_USERNAME:
    #         raise ForbiddenAppException()
