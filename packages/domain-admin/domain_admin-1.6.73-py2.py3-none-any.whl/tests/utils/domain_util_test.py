# -*- coding: utf-8 -*-
"""
@File    : domain_util_test.py
@Date    : 2022-10-22
@Author  : Peng Shiyu
"""
from __future__ import print_function, unicode_literals, absolute_import, division
import os
import unittest

from domain_admin.utils import domain_util


class DomainUtilTest(unittest.TestCase):
    def test_parse_domain(self):
        ret = domain_util.parse_domain('*.bnet.163.com')
        print(ret)

    def test_parse_domain_from_file(self):
        filename = '../domain.txt'

        if os.path.exists(filename):
            lst = domain_util.parse_domain_from_file(filename)
            for line in lst:
                print(line)

    def test_extract_domain(self):
        filename = '../domain.txt'

        if os.path.exists(filename):
            lst = domain_util.parse_domain_from_file(filename)
            for line in lst:
                print(domain_util.extract_domain(line))

    def test_parse_domain_from_txt_file(self):
        """
        测试域名解析函数
        :return:
        """
        domain_filename = '../domain.txt'
        domain_expect_filename = '../domain-expect.txt'

        expect_domains = None
        with open(domain_expect_filename, 'r') as f:
            expect_domains = [row.strip() for row in f.readlines()]

        if os.path.exists(domain_filename):
            lst = domain_util.parse_domain_from_txt_file(domain_filename)
            for index, row in enumerate(lst):
                assert row['domain'] == expect_domains[index]

    def test_is_ipv4(self):
        assert domain_util.is_ipv4('38.60.47.102') == True
        assert domain_util.is_ipv4('www.baidu.com') == False

    def test_get_root_domain(self):
        # print(domain_util.get_root_domain('38.60.47.102'))
        # print(domain_util.get_root_domain('www.baidu.com'))
        # print(domain_util.get_root_domain('www.baidu.com.cn'))
        print(domain_util.get_root_domain('xxx.com.de'))
        print(domain_util.get_root_domain('xxx.co.nl'))
        print(domain_util.get_root_domain('xxx.com.ru'))
        # assert domain_util.get_root_domain('www.baidu.com') == True

    def test_encode_hostname(self):
        assert domain_util.encode_hostname('www.baidu.com') == 'www.baidu.com'

        assert domain_util.encode_hostname('baidu.中国') == 'baidu.xn--fiqs8s'

        assert domain_util.encode_hostname('百度.中国') == 'xn--wxtr44c.xn--fiqs8s'

    def test_verify_cert_common_name(self):
        assert domain_util.verify_cert_common_name('chinafruitime.com', 'chinafruitime.com') is True
        assert domain_util.verify_cert_common_name('*.chinafruitime.com', 'chinafruitime.com') is True
        assert domain_util.verify_cert_common_name('*.chinafruitime.com', 'www.chinafruitime.com') is True
        assert domain_util.verify_cert_common_name('*.chinafruitime.com', 'blog.www.chinafruitime.com') is False
        assert domain_util.verify_cert_common_name('xxx.com', 'yyy.com') is False

    def test_get_domain_parent(self):
        assert domain_util.get_domain_parent('www.chinafruitime.com') == 'chinafruitime.com'
        assert domain_util.get_domain_parent('blog.www.chinafruitime.com') == 'www.chinafruitime.com'
        assert domain_util.get_domain_parent('ok.www.chinafruitime.com') == 'www.chinafruitime.com'
        assert domain_util.get_domain_parent('*.www.chinafruitime.com') == 'www.chinafruitime.com'
        assert domain_util.get_domain_parent('www') == ''
        assert domain_util.get_domain_parent('') == ''
