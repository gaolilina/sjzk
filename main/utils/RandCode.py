#!/usr/bin/env python
# coding: utf-8

from time import strftime, localtime
import urllib
import urllib.parse
import urllib.request
import json
import hmac
import hashlib


class RandCode(object):

    APP_ID = '414085560000257238'
    APP_SECRET = '0661fd8c18e40d60110020952ed6f454'
    ACCESS_TOKEN = ''
    RANDCODE_TOKEN = ''
    TOKEN_API = 'https://oauth.api.189.cn/emp/oauth2/v2/access_token'
    RANDCODE_TOKEN_API = 'http://api.189.cn/v2/dm/randcode/token'
    RANDCODE_SEND_API = 'http://api.189.cn/v2/dm/randcode/send'
    RANDCODE_SENDSMS_API = 'http://api.189.cn/v2/dm/randcode/sendSms'


    def __init__(self, app_id='', app_secret='', access_token=''):
        self.APP_ID = app_id or RandCode.APP_ID
        self.APP_SECRET = app_secret or RandCode.APP_SECRET
        self.ACCESS_TOKEN = access_token or self.__fetch_access_token()
        self.RANDCODE_TOKEN = self.__fetch_randcode_token()

    def send(self, phone, url, exp_time):
        result = False
        if self.ACCESS_TOKEN and self.RANDCODE_TOKEN:
            data = {
                'app_id':self.APP_ID,
				'access_token':self.ACCESS_TOKEN,
				'token':self.RANDCODE_TOKEN,
				'phone':phone,
				'url':url,
				'exp_time':exp_time,
				'timestamp':self.__date_time(),
				}
            data = self.__build_request_string(data)
            data = self.__data_sign(data)
            if data:
                res = self.__request_data('post', data, self.RANDCODE_SEND_API)
                json_data = json.loads(res)
                if json_data['res_code'] == 0:
                    result = True
        return result

    def send_sms(self, phone, randcode, exp_time='2'):
        result = False
        if self.ACCESS_TOKEN and self.RANDCODE_TOKEN:
            data = {
				'app_id':self.APP_ID,
				'access_token':self.ACCESS_TOKEN,
				'token':self.RANDCODE_TOKEN,
				'phone':phone,
				'randcode':str(randcode),
				'exp_time':exp_time,
				'timestamp':self.__date_time(),
				}
            data = self.__build_request_string(data)
            data = self.__data_sign(data)
            if data:
                res = self.__request_data(
                    'post', data, self.RANDCODE_SENDSMS_API)
                json_data = json.loads(res)
                if json_data['res_code'] == 0:
                    result = True
        return result

    def __request_data(self, method, data, url):
        if isinstance(data, dict):
            data = urllib.parse.urlencode(data).encode('utf-8')
        if method == 'post':
            req = urllib.request.Request(url, data)
        else:
            url = '%s?%s' % (url, data)
            req = urllib.request.Request(url)
        return urllib.request.urlopen(req).read().decode('utf-8')

    def __fetch_access_token(self):
        access_token = self.ACCESS_TOKEN
        if access_token == '':
            data = {
				'grant_type':'client_credentials',
				'app_id':self.APP_ID,
				'app_secret':self.APP_SECRET,
				}
            res = self.__request_data('post', data, self.TOKEN_API)
            json_data = json.loads(res)
            if json_data['res_code'] == '0':
                access_token = json_data['access_token']
            else:
                raise ValueError(json_data['res_message'])
        return access_token

    def __fetch_randcode_token(self):
        result = ''
        if self.ACCESS_TOKEN != '':
            data = {
				'app_id':self.APP_ID,
				'access_token':self.ACCESS_TOKEN,
				'timestamp':self.__date_time(),
				}
            data = self.__build_request_string(data)
            data = self.__data_sign(data)
            if data:
                res = self.__request_data('get', data, self.RANDCODE_TOKEN_API)
                json_data = json.loads(res)
                if json_data['res_code'] == 0:
                    result = json_data['token']
                else:
                    raise ValueError(json_data['res_message'])
        return result

    def __data_sign(self, data):
        result = ''
        if data:
            if isinstance(data, dict):
                data = self.__build_request_string(data)
                sign = hmac.new(self.APP_SECRET, urllib.parse.urlencode(data),
                                hashlib.sha1).digest()
            else:
                sign = hmac.new(self.APP_SECRET, data, hashlib.sha1).digest()
            result = "%s&sign=%s" % ( data, urllib.parse.quote(
                    sign.encode('base64').strip()) )
        return result

    def __build_request_string(self, dict):
        keys = sorted(dict)
        return '&'.join([ key + "=" + dict[key] for key in keys ])

    def __date_time(self):
        return strftime("%Y-%m-%d %H:%M:%S", localtime())



if __name__  == '__main__':
    r = RandCode('app_id', 'app_secret')
    r.send('phone number', 'http://yourdomain/rand_code.php', '3')
    r.send_sms('phone number', 189189)
