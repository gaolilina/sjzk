import urllib.parse
import httplib2


def send_message(data):
    http = httplib2.Http()
    url = 'https://d.apicloud.com/mcm/api/user/checkvercode'
    body = data
    headers = {"X-APICloud-AppId": "A6921645340532",
               "X-APICloud-AppKey": "DA69DA51-F088-AB2A-4B0F-19052E0C3570"}
    request, content=http.request(url, 'POST', headers=headers,
                 body=urllib.parse.urlencode(body))
    print (content)