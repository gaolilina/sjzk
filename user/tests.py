import datetime
import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TransactionTestCase, Client
from django.utils import timezone

from user.models import User, UserToken
from user.tools import encrypt_phone_info


def create_user(phone_number):
    with transaction.atomic():
        user = User(phone_number=phone_number)
        user.set_password('test')
        user.save()
        token_info = UserToken(user=user)
        token_info.update()
    return user


class UserTestCase(TransactionTestCase):
    def test_get_user_list(self):
        client = Client()
        users = []
        time = timezone.now()
        for i in range(32):
            user = create_user(str(i))
            user.name = 'User %s' % i
            user.create_time = time
            user.save()
            time = time + datetime.timedelta(seconds=10)
            users.append(user)
        token = users[0].token_info.token

        # get total
        r = client.get(reverse('user:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 32)

        # get all by 'create_time'
        data = json.dumps({'offset': 0, 'limit': 100, 'order': 1})
        r = client.get(reverse('user:root'), {'token': token, 'data': data})
        result = json.loads(r.content.decode('utf8'))
        self.assertEqual(result[12]['name'], 'User 12')
        self.assertEqual(result[24]['name'], 'User 24')

        # disable users[10] then get total
        users[10].is_enabled = False
        users[10].save()
        r = client.get(reverse('user:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)

    def test_register(self):
        client = Client()
        phone_info = encrypt_phone_info('13010101010')
        data = json.dumps({'phone_info': phone_info, 'password': 'password'})

        r = client.post(reverse('user:root'), {'data': data})
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content.decode('utf8'))['token']
        token = UserToken.objects.select_related('user').get(
            user__phone_number='13010101010').token
        self.assertEqual(result, token)

    def test_get_token(self):
        client = Client()
        user = create_user('11111111111')
        user.username = 'test'
        user.set_password('test')
        user.save()

        # get by phone number
        data = json.dumps({'username': '11111111111', 'password': 'test'})
        r = client.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

        # get by username
        data = json.dumps({'username': 'test', 'password': 'test'})
        r = client.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

    def test_check_and_set_username(self):
        client = Client()
        user = create_user('1')
        token = user.token_info.token

        # get username
        r = client.get(reverse('user:username'), {'token': token})
        result = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(result, None)

        # set username
        data = json.dumps({'username': 'test_user'})
        r = client.post(
            reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 200)

        # get username
        r = client.get(reverse('user:username'), {'token': token})
        result = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(result, 'test_user')

        # try to change username
        data = json.dumps({'username': 'testuser'})
        r = client.post(
            reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 403)

        # set existed username
        user = create_user('2')
        token = user.token_info.token
        data = json.dumps({'username': 'test_user'})
        r = client.post(
            reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 400)

        # set pure-digit username
        user = create_user('3')
        token = user.token_info.token
        data = json.dumps({'username': '13010101010'})
        r = client.post(
            reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 400)

    def test_set_and_change_password(self):
        client = Client()
        user = create_user('1')
        token = user.token_info.token

        # change password
        data = json.dumps({'password': 'testPass', 'old_password': 'test'})
        r = client.post(reverse('user:password'),
                        {'token': token, 'data': data})
        self.assertEqual(r.status_code, 200)

        # get token by new password
        data = json.dumps({'username': '1', 'password': 'testPass'})
        r = client.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

        # change password / invalid old_password
        data = json.dumps({'password': 'changePass!', 'old_password': 'what'})
        r = client.post(reverse('user:password'),
                        {'token': token, 'data': data})
        self.assertEqual(r.status_code, 403)

        # change password / invalid password
        data = json.dumps({'password': 'short', 'old_password': 'testPass!'})
        r = client.post(reverse('user:password'),
                        {'token': token, 'data': data})
        self.assertEqual(r.status_code, 400)
