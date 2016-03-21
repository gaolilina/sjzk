import datetime
import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TestCase, Client
from django.utils import timezone

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
    def test_get_user_list(self):
        client = Client()
        users = []
        time = timezone.now()
        for i in range(32):
            user = create_user(str(i+1), str(i+1))
            user.name = 'User %s' % str(i+1)
            user.create_time = time
            user.save()
            time = time + datetime.timedelta(seconds=10)
            users.append(user)
        token = users[0].token_info.token

        # get total
        response = client.get(reverse('user:total'), {'token': token})
        total = json.loads(response.content.decode('utf8'))['total']
        self.assertEqual(total, 32)

        # get 15-20 by 'create_time'
        data = json.dumps({'offset': 14, 'limit': 6, 'order': 1})
        response = client.get(reverse('user:root'),
                              {'token': token, 'data': data})
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(result[0]['name'], 'User 15')
        self.assertEqual(result[5]['name'], 'User 20')

        # get 32 by '-name'
        data = json.dumps({'offset': 31, 'limit': 1, 'order': 3})
        response = client.get(reverse('user:root'),
                              {'token': token, 'data': data})
        result = json.loads(response.content.decode('utf8'))
        self.assertEqual(result[0]['name'], 'User 1')

    def test_get_token(self):
        client = Client()
        user = create_user('11111111111', '101010101010101')
        user.username = 'test'
        user.set_password('test')
        user.save()

        # get by phone info
        phone_info = encrypt_phone_info('11111111111', '101010101010101')
        data = json.dumps({'method': 0, 'phone_info': phone_info})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user.token_info.refresh_from_db()
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by phone number
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
        data = json.dumps({'method': 2, 'username': 'test', 'password': 'test'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 200)
        user.token_info.refresh_from_db()
        token = user.token_info.token
        content = json.loads(response.content.decode('utf8'))
        self.assertEqual(content['token'], token)

        # get by phone info / auto register
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
        phone_info = encrypt_phone_info('22222222222', '000000010000000')
        data = json.dumps({'method': 0, 'phone_info': phone_info})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)

        # get by phone number / invalid
        data = json.dumps(
            {'method': 1, 'phone_number': '22222222222', 'password': 'none'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)

        # get by username / invalid
        data = json.dumps(
            {'method': 2, 'username': 'none', 'password': 'none'})
        response = client.post(reverse('user:token'), {'data': data})
        status_code = response.status_code
        self.assertEqual(status_code, 403)

    def test_check_and_set_username(self):
        client = Client()
        user = create_user('1', '1')
        token = user.token_info.token

        # set username with invalid character
        data = json.dumps({'username': '中文username'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 400)

        # set username unmet length requirement
        data = json.dumps({'username': '中文username'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 400)
        data = json.dumps({'username': 'loooooooooooooooooooong_username'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 400)

        # set username
        data = json.dumps({'username': 'username'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 200)

        # get username
        response = client.get(reverse('user:username'), {'token': token})
        result = json.loads(response.content.decode('utf8'))['username']
        self.assertEqual(result, 'username')

        # set username again
        data = json.dumps({'username': 'nameuser'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 403)

        # set existed username
        user = create_user('2', '2')
        token = user.token_info.token
        client = Client()
        data = json.dumps({'username': 'username'})
        response = client.post(reverse('user:username'),
                               {'data': data, 'token': token})
        self.assertEqual(response.status_code, 400)

    def test_set_and_change_password(self):
        client = Client()
        user = create_user('1', '1')
        token = user.token_info.token

        # before
        response = client.get(reverse('user:password'), {'token': token})
        has_password = json.loads(
            response.content.decode('utf8'))['has_password']
        self.assertEqual(has_password, False)

        # set password
        data = json.dumps({'password': 'testPass'})
        response = client.post(reverse('user:password'),
                               {'token': token, 'data': data})
        self.assertEqual(response.status_code, 200)

        # after
        response = client.get(reverse('user:password'), {'token': token})
        has_password = json.loads(
            response.content.decode('utf8'))['has_password']
        self.assertEqual(has_password, True)

        # change password
        data = json.dumps({'password': 'testPass!', 'old_password': 'testPass'})
        response = client.post(reverse('user:password'),
                               {'token': token, 'data': data})
        self.assertEqual(response.status_code, 200)

        # change password / invalid old_password
        data = json.dumps({'password': 'changePass!', 'old_password': ''})
        response = client.post(reverse('user:password'),
                               {'token': token, 'data': data})
        self.assertEqual(response.status_code, 403)

        # change password / invalid password
        data = json.dumps({'password': 'short', 'old_password': 'testPass!'})
        response = client.post(reverse('user:password'),
                               {'token': token, 'data': data})
        self.assertEqual(response.status_code, 400)
