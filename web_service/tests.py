from django.http import HttpResponse, HttpRequest
from django.test import TestCase

from user.models import User, UserToken
from web_service.decorators import web_service


@web_service(require_token=False)
def dummy_view(request, data):
    content = ''
    for k, v in data.items():
        content += '%s %s\n' % (k, v)
    return HttpResponse(content)


@web_service(method='GET')
def dummy_view_require_token(request):
    content = 'OK'
    return HttpResponse(content)


class WebServiceTestCase(TestCase):
    def test_dummy_view(self):
        request = HttpRequest()
        request.method = 'POST'
        request.POST['data'] = '{"a": "A", "b": "B"}'
        response = dummy_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'a A\nb B\n')

    def test_dummy_view_require_token(self):
        u = User(name='test', phone_number='test', imei='test')
        u.save()
        ut = UserToken(user=u)
        ut.update()

        request = HttpRequest()
        request.method = 'GET'
        request.GET['token'] = ut.token
        response = dummy_view_require_token(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
