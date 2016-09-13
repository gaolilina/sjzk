# -*- coding: utf-8 -*-
import top
import top.api

'''
这边可以设置一个默认的appkey和secret，当然也可以不设置
注意：默认的只需要设置一次就可以了

'''
#top.appinfo("23449950", "8af97d379aa5df46ceed21b2ff4b3b13")

'''
使用自定义的域名和端口（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com",80)

使用自定义的域名（测试沙箱环境使用）
a = top.api.UserGetRequest("gw.api.tbsandbox.com")

使用默认的配置（调用线上环境）
a = top.api.UserGetRequest()

'''
# a = top.api.UserGetRequest()
url = 'gw.api.taobao.com'
port = 80
appkey = '23449950'
secret = '8af97d379aa5df46ceed21b2ff4b3b13'
a = top.api.OpenimUsersGetRequest()
a.set_app_info(top.appinfo(appkey, secret))
'''
可以在运行期替换掉默认的appkey和secret的设置
a.set_app_info(top.appinfo("appkey","*******"))
'''

# a.fields = "nick"
a.userids = "abc"

try:
    f = a.getResponse()
    print(f)
except Exception as e:
    print(e)
