# -*- coding: utf-8 -*-
"""
@File    : cert_service.py
@Date    : 2024-08-05
"""

from domain_admin.utils import domain_util
from domain_admin.utils.cert_util import cert_openssl_v2, cert_common


def get_cert_information(domain):
    """
    获取域名证书信息
    :return:
    """

    # 解析域名
    resolve_domain = domain_util.parse_domain(domain)

    cert = cert_openssl_v2.get_ssl_cert(resolve_domain)
    parsed_cert = cert_common.parse_cert(cert)
    cert_pem = cert_common.dump_certificate_to_pem(cert)
    cert_text = cert_common.dump_certificate_to_text(cert)

    return {
        'resolve_domain': resolve_domain,
        'parsed_cert': parsed_cert.to_dict() if parsed_cert else parsed_cert,
        'cert_pem': cert_pem,
        'cert_text': cert_text,
    }
