import json

from django.http import JsonResponse, HttpResponse, HttpRequest
from django.test import TestCase

from user.models import User, UserToken
from web_service.decorators import web_service


@web_service(require_token=False)
def dummy_view(request, data):
    return JsonResponse(data)


@web_service(method='GET')
def dummy_view_require_token(request):
    content = 'OK'
    return HttpResponse(content)


class WebServiceTestCase(TestCase):
    def test_dummy_view(self):
        request = HttpRequest()
        request.method = 'POST'
        data = {"a": "A", "b": "B"}
        request.POST['data'] = json.dumps(data)
        response = dummy_view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content.decode('utf8')), data)

    def test_dummy_view_require_token(self):
        u = User(name='test', phone_number='test')
        u.save()
        ut = UserToken(user=u)
        ut.update()

        request = HttpRequest()
        request.method = 'GET'
        request.GET['token'] = ut.token
        response = dummy_view_require_token(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
