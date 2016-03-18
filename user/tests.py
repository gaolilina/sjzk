import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase, Client

from user import encrypt_phone_info
from user.models import User, UserToken


def create_user(phone_number, imei):
    with transaction.atomic():
        name = '新用户%s' % phone_number[-4:]
        user = User(phone_number=phone_number, imei=imei, name=name)
        user.save()
        token_info = UserToken(user=user)
        token_info.update()
    return user


class UserTestCase(TestCase):
    def test_token(self):
        user = create_user('11111111111', '101010101010101')
        user.username = 'test'
        user.set_password('test')
        user.save()

        # get by phone info
        phone_info = encrypt_phone_info('11111111111', '101010101010101')
        data = json.dumps({'method': 0, 'phone_info': phone_info})
        client = Client()
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user.token_info.refresh_from_db()
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by phone number
        client = Client()
        data = json.dumps(
            {'method': 1, 'phone_number': '11111111111', 'password': 'test'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user.token_info.refresh_from_db()
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by username
        client = Client()
        data = json.dumps({'method': 2, 'username': 'test', 'password': 'test'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user.token_info.refresh_from_db()
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by phone info / auto register
        client = Client()
        phone_info = encrypt_phone_info('22222222222', '000000000000000')
        data = json.dumps({'method': 0, 'phone_info': phone_info})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user = User.objects.get(phone_number='22222222222')
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by phone info / invalid
        client = Client()
        phone_info = encrypt_phone_info('22222222222', '000000010000000')
        data = json.dumps({'method': 0, 'phone_info': phone_info})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)

        # get by phone number / invalid
        client = Client()
        data = json.dumps(
            {'method': 1, 'phone_number': '22222222222', 'password': 'none'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)

        # get by username / invalid
        client = Client()
        data = json.dumps(
            {'method': 2, 'username': 'none', 'password': 'none'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)
