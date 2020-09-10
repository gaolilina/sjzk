#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import urllib.parse
import urllib.request


def send_message(mobile, tpl_value, m="GET"):
    """第三方短信调用api"""
    data = dict()
    data['tpl_id'] = "30517"
    data['key'] = 'c2b426f88a99c9fdf9a2a55d617e4f0d'
    data['mobile'] = mobile
    data['tpl_value'] = tpl_value
    params = urllib.parse.urlencode(data)
    url = "http://v.juhe.cn/sms/send"
    if m == "GET":
        urllib.request.urlopen("%s?%s" % (url, params))
    else:
        urllib.request.urlopen(url, params)
