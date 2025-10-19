# -*- coding: utf-8 -*-
"""
domain_info_api.py
"""
from __future__ import print_function, unicode_literals, absolute_import, division

import json
from datetime import datetime
from operator import itemgetter

from flask import request, g
from peewee import fn
from playhouse.shortcuts import model_to_dict

from domain_admin.enums.operation_enum import OperationEnum
from domain_admin.enums.role_enum import RoleEnum
from domain_admin.model.domain_info_model import DomainInfoModel
from domain_admin.model.domain_model import DomainModel
from domain_admin.model.group_model import GroupModel
from domain_admin.model.group_user_model import GroupUserModel
from domain_admin.service import domain_info_service, async_task_service, file_service, group_service, \
    operation_service, group_user_service, domain_service, common_service, domain_icp_service, tag_service, auth_service
from domain_admin.utils import domain_util, time_util, icp_util
from domain_admin.utils.flask_ext.app_exception import AppException, DataNotFoundAppException
from domain_admin.utils.open_api import crtsh_api


@auth_service.permission(role=RoleEnum.USER)
@operation_service.operation_log_decorator(
    model=DomainInfoModel,
    operation_type_id=OperationEnum.CREATE,
    primary_key='domain_info_id'
)
def add_domain_info():
    """
    添加域名
    :return:
    """

    current_user_id = g.user_id

    domain = domain_util.get_root_domain(request.json['domain'])
    domain_start_time = request.json.get('domain_start_time')
    domain_expire_time = request.json.get('domain_expire_time')
    is_auto_update = request.json.get('is_auto_update', True)
    is_auto_subdomain = request.json.get('is_auto_subdomain', False)
    comment = request.json.get('comment', '')
    tags = request.json.get('tags')
    icp_company = request.json.get('icp_company', '')
    icp_licence = request.json.get('icp_licence', '')
    group_id = request.json.get('group_id') or 0
    user_id = request.json.get('user_id')

    row = domain_info_service.add_domain_info(
        domain=domain,
        domain_start_time=domain_start_time,
        domain_expire_time=domain_expire_time,
        comment=comment,
        tags=tags,
        group_id=group_id,
        user_id=user_id or current_user_id,
        icp_company=icp_company,
        icp_licence=icp_licence,
        is_auto_update=is_auto_update
    )

    # 异步提交
    if is_auto_subdomain:
        domain_service.auto_import_from_domain_async(
            root_domain=domain,
            group_id=group_id,
            user_id=current_user_id
        )
        # async_task_service.submit_task(
        #     fn=domain_service.auto_import_from_domain,
        #     root_domain=domain,
        #     group_id=group_id,
        #     user_id=current_user_id
        # )

    tag_service.add_tags(tags)

    return {'domain_info_id': row.id}


@auth_service.permission(role=RoleEnum.USER)
@operation_service.operation_log_decorator(
    model=DomainInfoModel,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='domain_info_id'
)
def update_domain_info_by_id():
    """
    更新数据
    :return:
    """

    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']

    domain = domain_util.get_root_domain(request.json['domain'])
    domain_start_time = request.json.get('domain_start_time')
    domain_expire_time = request.json.get('domain_expire_time')
    is_auto_update = request.json.get('is_auto_update', True)
    is_auto_subdomain = request.json.get('is_auto_subdomain', False)
    comment = request.json.get('comment', '')
    group_id = request.json.get('group_id') or 0
    tags = request.json.get('tags')
    icp_company = request.json.get('icp_company', '')
    icp_licence = request.json.get('icp_licence', '')
    user_id = request.json.get('user_id')

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    # is_auto_update = request.json.get('is_auto_update', True)
    # is_expire_monitor = request.json.get('is_expire_monitor', True)

    data = {
        'domain': domain,
        'comment': comment,
        'group_id': group_id,
        'tags_raw': json.dumps(tags, ensure_ascii=False),
        'icp_company': icp_company,
        'icp_licence': icp_licence,
        'is_auto_update': is_auto_update
    }

    # 不自动更新，才可以提交开始时间和结束时间
    if is_auto_update is False:
        data['domain_start_time'] = domain_start_time
        data['domain_expire_time'] = domain_expire_time

        if domain_expire_time:
            data['domain_expire_days'] = time_util.get_diff_days(datetime.now(),
                                                                 time_util.parse_time(domain_expire_time))
        else:
            data['domain_expire_days'] = 0

    if user_id:
        data['user_id'] = user_id

    DomainInfoModel.update(data).where(
        DomainInfoModel.id == domain_info_id
    ).execute()

    if domain_info_row.domain != domain and is_auto_update:
        # 需要自动更新
        domain_info_service.update_domain_info_row(domain_info_row)

    if is_auto_subdomain:
        domain_service.auto_import_from_domain_async(
            root_domain=domain,
            group_id=group_id,
            user_id=current_user_id
        )
        #
        # async_task_service.submit_task(
        #     fn=domain_service.auto_import_from_domain,
        #     root_domain=domain,
        #     group_id=group_id,
        #     user_id=current_user_id
        # )

    tag_service.add_tags(tags)


@auth_service.permission(role=RoleEnum.USER)
@operation_service.operation_log_decorator(
    model=DomainInfoModel,
    operation_type_id=OperationEnum.UPDATE,
    primary_key='domain_info_id'
)
def update_domain_info_field_by_id():
    """
    更新单个数据
    :return:
    """

    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']
    field = request.json.get('field')
    value = request.json.get('value')

    if field not in ['is_auto_update', 'is_expire_monitor']:
        raise AppException("not allow field")

    data = {
        field: value,
    }

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    DomainInfoModel.update(data).where(
        DomainInfoModel.id == domain_info_row.id
    ).execute()


@auth_service.permission(role=RoleEnum.USER)
@operation_service.operation_log_decorator(
    model=DomainInfoModel,
    operation_type_id=OperationEnum.DELETE,
    primary_key='domain_info_id'
)
def delete_domain_info_by_id():
    """
    删除
    :return:
    """
    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    DomainInfoModel.delete_by_id(domain_info_row.id)


@auth_service.permission(role=RoleEnum.USER)
@operation_service.operation_log_decorator(
    model=DomainInfoModel,
    operation_type_id=OperationEnum.BATCH_DELETE,
    primary_key='domain_info_ids'
)
def delete_domain_info_by_ids():
    """
    批量删除
    """
    current_user_id = g.user_id

    domain_info_ids = request.json['domain_info_ids']

    DomainInfoModel.delete().where(
        DomainInfoModel.id.in_(domain_info_ids),
        DomainInfoModel.user_id == current_user_id
    ).execute()


@auth_service.permission(role=RoleEnum.USER)
def get_domain_info_by_id():
    """
    获取
    :return:
    """
    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    domain_row = model_to_dict(
        model=domain_info_row,
        extra_attrs=[
            'real_domain_expire_days',
            'update_time_label',
            'tags',
        ],
        exclude=['tags_raw'],
    )

    # 主机数量
    ssl_count = DomainModel.select().where(
        DomainModel.root_domain == domain_row['domain'],
        DomainModel.user_id == current_user_id
    ).count()

    domain_row['ssl_count'] = ssl_count
    domain_row['group_name'] = group_service.get_group_name_by_id(domain_row['group_id'])

    # 编辑权限
    group_user_permission_map = group_user_service.get_group_user_permission_map(current_user_id)

    if domain_row['user_id'] == current_user_id:
        has_edit_permission = True
    else:
        has_edit_permission = group_user_permission_map.get(domain_row['group_id'], False)

    domain_row['has_edit_permission'] = has_edit_permission

    common_service.load_user_name([domain_row])

    return domain_row


@auth_service.permission(role=RoleEnum.USER)
def update_domain_info_row_by_id():
    """
    更新当前行的域名信息
    :return:
    """
    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    domain_info_service.update_domain_info_row(row=domain_info_row)


@auth_service.permission(role=RoleEnum.USER)
def update_all_domain_info_of_user():
    """
    更新当前用户的域名信息
    :return:
    """
    current_user_id = g.user_id

    domain_info_service.update_all_domain_info_of_user(user_id=current_user_id)
    # async_task_service.submit_task(fn=domain_info_service.update_all_domain_info_of_user, user_id=current_user_id)


@auth_service.permission(role=RoleEnum.USER)
def update_all_domain_icp_of_user():
    """
    更新当前用户的域名icp信息
    :return:
    """
    current_user_id = g.user_id

    domain_info_service.update_all_domain_icp_of_user(current_user_id)

    # async_task_service.submit_task(fn=domain_info_service.update_all_domain_icp_of_user, user_id=current_user_id)


@auth_service.permission(role=RoleEnum.USER)
def update_domain_row_icp():
    """
    更新当前域名icp信息
    :return:
    """
    current_user_id = g.user_id

    domain_info_id = request.json['domain_info_id']

    # check data
    domain_info_row = DomainInfoModel.select().where(
        DomainInfoModel.id == domain_info_id,
        DomainInfoModel.user_id == current_user_id
    ).first()

    if not domain_info_row:
        raise DataNotFoundAppException()

    domain_info_service.update_domain_row_icp(row=domain_info_row)


@auth_service.permission(role=RoleEnum.USER)
def import_domain_info_from_file():
    """
    从文件导入域名
    支持格式: txt、xlsx、csv
    :return:
    """
    current_user_id = g.user_id

    update_file = request.files.get('file')

    filename = file_service.save_temp_file(update_file)

    # 导入数据
    domain_info_service.add_domain_from_file(filename, current_user_id)

    # 异步查询
    domain_info_service.handle_auto_import_domain_info(current_user_id)
    # async_task_service.submit_task(fn=domain_info_service.update_all_domain_info_of_user, user_id=current_user_id)


@auth_service.permission(role=RoleEnum.USER)
def export_domain_info_file():
    """
    导出域名文件
    csv格式
    :return:
    """
    current_user_id = g.user_id

    keyword = request.json.get('keyword')
    group_ids = request.json.get('group_ids')
    domain_expire_days = request.json.get('domain_expire_days')
    role = request.json.get('role')
    ext = request.json.get('ext', 'csv')

    order_prop = request.json.get('order_prop') or 'domain_expire_days'
    order_type = request.json.get('order_type') or 'ascending'

    params = {
        'keyword': keyword,
        'group_ids': group_ids,
        'domain_expire_days': domain_expire_days,
        'role': role,
        'user_id': current_user_id
    }

    # 列表数据
    query = domain_info_service.get_domain_info_query(**params)

    ordering = domain_info_service.get_ordering(order_prop=order_prop, order_type=order_type)

    rows = query.order_by(*ordering)

    lst = [model_to_dict(
        model=row,
        extra_attrs=[
            'domain_start_date',
            'domain_expire_date',
            'real_domain_expire_days',
            'update_time_label',
            'tags',
            'tags_str',
        ]
    ) for row in rows]

    # 分组名
    group_service.load_group_name(lst)

    filename = domain_info_service.export_domain_to_file(ext=ext, rows=lst)

    return {
        'name': filename,
        'url': file_service.resolve_temp_url(filename)
    }


@auth_service.permission(role=RoleEnum.USER)
def get_domain_info_list():
    """
    获取域名列表
    :return:
    """
    current_user_id = g.user_id

    page = request.json.get('page', 1)
    size = request.json.get('size', 10)

    keyword = request.json.get('keyword')
    group_ids = request.json.get('group_ids')
    domain_expire_days = request.json.get('domain_expire_days')
    role = request.json.get('role')

    order_prop = request.json.get('order_prop') or 'domain_expire_days'
    order_type = request.json.get('order_type') or 'ascending'

    group_user_permission_map = {}

    if role == RoleEnum.ADMIN:
        pass

    else:
        # 所在分组
        group_user_rows = GroupUserModel.select().where(
            GroupUserModel.user_id == current_user_id
        )

        group_user_list = list(group_user_rows)
        # 组员权限
        group_user_permission_map = {row.group_id: row.has_edit_permission for row in group_user_list}

    params = {
        'keyword': keyword,
        'group_ids': group_ids,
        'domain_expire_days': domain_expire_days,
        'role': role,
        'user_id': current_user_id
    }

    # 列表数据
    query = domain_info_service.get_domain_info_query(**params)

    total = query.count()

    lst = []
    if total > 0:

        ordering = domain_info_service.get_ordering(order_prop=order_prop, order_type=order_type)

        rows = query.order_by(*ordering).paginate(page, size)

        lst = [model_to_dict(
            model=row,
            extra_attrs=[
                'real_domain_expire_days',
                'update_time_label',
                'tags',
            ]
        ) for row in rows]

        domain_list = [row['domain'] for row in lst]

        # 域名证书
        root_domain_groups = DomainModel.select(
            DomainModel.root_domain,
            fn.COUNT(DomainModel.id).alias('count')
        ).where(
            DomainModel.root_domain.in_(domain_list),
            DomainModel.user_id == current_user_id
        ).group_by(DomainModel.root_domain)

        root_domain_groups_map = {
            row.root_domain: row.count
            for row in root_domain_groups
        }

        for row in lst:
            row['ssl_count'] = root_domain_groups_map.get(row['domain'], 0)

            if role == RoleEnum.ADMIN:
                has_edit_permission = True

            elif row['user_id'] == current_user_id:
                has_edit_permission = True
            else:
                has_edit_permission = group_user_permission_map.get(row['group_id'], False)

            row['has_edit_permission'] = has_edit_permission

        # 分组名
        group_service.load_group_name(lst)
        # 用户名
        common_service.load_user_name(lst)

    return {
        'list': lst,
        'total': total,
    }


@auth_service.permission(role=RoleEnum.USER)
def get_domain_info_group_filter():
    """
    获取域名分组筛选器
    :return:
    """

    current_user_id = g.user_id

    # 分组列表数据
    query = GroupModel.select().where(
        GroupModel.user_id == current_user_id
    )

    total = query.count()
    lst = []
    if total > 0:

        # 证书分组统计
        cert_groups = DomainInfoModel.select(
            DomainInfoModel.group_id,
            fn.COUNT(DomainInfoModel.id).alias('count')
        ).group_by(DomainInfoModel.group_id)

        groups_map = {
            str(row.group_id): row.count
            for row in cert_groups
        }

        lst = []
        for row in query:
            row_dict = model_to_dict(row)
            row_dict['domain_count'] = groups_map.get(str(row.id), 0)
            lst.append(row_dict)

        if groups_map.get('0'):
            lst.append({
                'domain_count': groups_map.get('0'),
                'id': 0,
                'name': '未分组',
            })

        lst.sort(key=itemgetter('domain_count'), reverse=True)

    return {
        'list': lst,
        'total': len(lst),
    }


@auth_service.permission(role=RoleEnum.USER)
def get_icp():
    """
    查询icp信息
    """
    domain = request.json['domain']

    # 解析域名
    resolve_domain = domain_util.parse_domain(domain)

    item = domain_icp_service.get_domain_icp(resolve_domain)

    if not item:
        raise AppException('没有查到icp信息')

    res = item.to_dict()
    res['resolve_domain'] = resolve_domain

    return res


@auth_service.permission(role=RoleEnum.USER)
def get_sub_domain_cert():
    """
    获取子域证书列表
    :return:
    """
    keyword = request.json.get('keyword', 1)

    lst = crtsh_api.search(keyword)

    return {
        'list': lst,
        'total': len(lst)
    }


@auth_service.permission(role=RoleEnum.USER)
def auto_import_subdomain_by_ids():
    """
    批量导入子域证书
    @since v1.6.30
    :return:
    """
    current_user_id = g.user_id

    domain_ids = request.json['domain_ids']

    rows = DomainInfoModel.select().where(
        DomainInfoModel.id.in_(domain_ids),
        DomainInfoModel.user_id == current_user_id
    )

    # 异步提交
    domain_service.auto_import_from_domain_batch_async(rows=rows, user_id=current_user_id)
