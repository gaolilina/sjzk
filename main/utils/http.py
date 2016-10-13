import urllib.parse
import urllib.request
import httplib2


'''
def send_message(data):
    http = httplib2.Http()
    url = 'https://d.apicloud.com/mcm/api/user/checkvercode'
    body = data
    headers = {"X-APICloud-AppId": "A6921645340532",
               "X-APICloud-AppKey": "DA69DA51-F088-AB2A-4B0F-19052E0C3570"}
    http.request(url, 'POST', headers=headers,
                 body=urllib.parse.urlencode(body)
'''


def send_message(data):
    data['uid'] = 'zq353996852'
    data['pwd'] = 'c334c800ae8802557106fe09d70f3eb8'
    data['template'] = '100006'
    params = urllib.parse.urlencode(data)
    print(params)
    f = urllib.request.urlopen(
        "http://api.sms.cn/sms/?ac=send?%s" % params)
    print(f)
    print(f.read())
