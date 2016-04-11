import datetime
import json

from django.core.urlresolvers import reverse
from django.db import transaction
from django.test import TransactionTestCase, Client
from django.utils import timezone

from location.models import Province, City
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
        c = Client()
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
        r = c.get(reverse('user:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 32)

        # get all by 'create_time'
        data = json.dumps({'offset': 0, 'limit': 100, 'order': 1})
        r = c.get(reverse('user:root'), {'token': token, 'data': data})
        result = json.loads(r.content.decode('utf8'))
        self.assertEqual(result[12]['name'], 'User 12')
        self.assertEqual(result[24]['name'], 'User 24')

        # disable users[10] then get total
        users[10].is_enabled = False
        users[10].save()
        r = c.get(reverse('user:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)

    def test_register(self):
        c = Client()
        phone_info = encrypt_phone_info('13010101010')
        data = json.dumps({'phone_info': phone_info, 'password': 'password'})

        r = c.post(reverse('user:root'), {'data': data})
        self.assertEqual(r.status_code, 200)
        result = json.loads(r.content.decode('utf8'))['token']
        token = UserToken.objects.select_related('user').get(
            user__phone_number='13010101010').token
        self.assertEqual(result, token)

    def test_get_token(self):
        c = Client()
        user = create_user('11111111111')
        user.username = 'test'
        user.set_password('test')
        user.save()

        # get by phone number
        data = json.dumps({'username': '11111111111', 'password': 'test'})
        r = c.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

        # get by username
        data = json.dumps({'username': 'test', 'password': 'test'})
        r = c.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

    def test_check_and_set_username(self):
        c = Client()
        user = create_user('1')
        token = user.token_info.token

        # get username
        r = c.get(reverse('user:username'), {'token': token})
        result = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(result, None)

        # set username
        data = json.dumps({'username': 'test_user'})
        r = c.post(reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 200)

        # get username
        r = c.get(reverse('user:username'), {'token': token})
        result = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(result, 'test_user')

        # try to change username
        data = json.dumps({'username': 'testuser'})
        r = c.post(reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 403)

        # set existed username
        user = create_user('2')
        token = user.token_info.token
        data = json.dumps({'username': 'test_user'})
        r = c.post(reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 400)

        # set pure-digit username
        user = create_user('3')
        token = user.token_info.token
        data = json.dumps({'username': '13010101010'})
        r = c.post(reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 400)

    def test_set_and_change_password(self):
        c = Client()
        user = create_user('1')
        token = user.token_info.token

        # change password
        data = json.dumps({'password': 'testPass', 'old_password': 'test'})
        r = c.post(reverse('user:password'), {'token': token, 'data': data})
        self.assertEqual(r.status_code, 200)

        # get token by new password
        data = json.dumps({'username': '1', 'password': 'testPass'})
        r = c.post(reverse('user:token'), {'data': data})
        token = UserToken.objects.get(user=user).token
        result = json.loads(r.content.decode('utf8'))['token']
        self.assertEqual(result, token)

        # change password / invalid old_password
        data = json.dumps({'password': 'changePass!', 'old_password': 'what'})
        r = c.post(reverse('user:password'), {'token': token, 'data': data})
        self.assertEqual(r.status_code, 403)

        # change password / invalid password
        data = json.dumps({'password': 'short', 'old_password': 'testPass!'})
        r = c.post(reverse('user:password'), {'token': token, 'data': data})
        self.assertEqual(r.status_code, 400)

    def test_set_and_get_profile(self):
        # prepare test data
        user = create_user('11111111111')
        token = user.token_info.token
        province = Province(name='天际省')
        province.save()
        city = City(name='雪漫城', province=province)
        city.save()
        data = {
            'name': '龙裔',
            'description': 'Fus Ro Dah!',
            'email': 'dragonborn@skyrim',
            'gender': 1,
            'birthday': '1990-01-01',
            'location': [province.id, city.id],
            'tags': ['Nord', 'Warrior', 'Two-handed'],
        }
        data = json.dumps(data)

        c = Client()

        # set profile
        r = c.post(reverse('user:profile'), {'token': token, 'data': data})
        self.assertEqual(r.status_code, 200)
        data = json.dumps({'username': 'dragonborn'})
        r = c.post(reverse('user:username'), {'data': data, 'token': token})
        self.assertEqual(r.status_code, 200)

        # get profile
        r = c.get(reverse('user:profile'), {'token': token})
        self.assertEqual(r.status_code, 200)
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['username'], 'dragonborn')
        self.assertEqual(r['name'], '龙裔')
        self.assertEqual(r['description'], 'Fus Ro Dah!')
        self.assertEqual(r['email'], 'dragonborn@skyrim')
        self.assertEqual(r['gender'], 1)
        self.assertEqual(r['birthday'], '1990-01-01')
        self.assertEqual(r['location'], [province.id, city.id])
        self.assertEqual(r['tags'], ['Nord', 'Warrior', 'Two-handed'])

        user_id = user.id
        # now try get and set profile above from another user
        user = create_user('21111111111')
        token = user.token_info.token
        r = c.get(
            reverse('user:profile_id', kwargs={'user_id': user_id}),
            {'token': token})
        self.assertEqual(r.status_code, 200)

        data = json.dumps({'name': '抓根宝'})
        r = c.post(
            reverse('user:profile_id', kwargs={'user_id': user_id}),
            {'token': token, 'data': data})
        self.assertEqual(r.status_code, 403)

    def test_tag(self):
        # prepare user
        user = create_user('1')
        token = user.token_info.token

        c = Client()
        # get tag for first time
        r = c.get(reverse('user:profile'), {'token': token})
        tags = json.loads(r.content.decode('utf8'))['tags']
        self.assertEqual(tags, [])

        # set 5 tags
        data = json.dumps({'tags': ['t1', 't2', 't3', 't4', 't5']})
        c.post(reverse('user:profile'), {'token': token, 'data': data})

        # then set 2 tags
        data = json.dumps({'tags': ['t6', 't3']})
        c.post(reverse('user:profile'), {'token': token, 'data': data})
        r = c.get(reverse('user:profile'), {'token': token})
        tags = json.loads(r.content.decode('utf8'))['tags']
        self.assertEqual(tags, ['t6', 't3'])

        # then clear all tags
        data = json.dumps({'tags': []})
        c.post(reverse('user:profile'), {'token': token, 'data': data})
        r = c.get(reverse('user:profile'), {'token': token})
        tags = json.loads(r.content.decode('utf8'))['tags']
        self.assertEqual(tags, [])

    def test_location(self):
        # prepare data
        p1 = Province(name='P1')
        p1.save()
        c1 = City(province=p1, name='c1')
        c1.save()
        user = create_user('1')
        token = user.token_info.token
        c = Client()

        # set province and city
        data = json.dumps({'location': [p1.id, c1.id]})
        c.post(reverse('user:profile'), {'token': token, 'data': data})

        # clear city
        data = json.dumps({'location': [p1.id, None]})
        c.post(reverse('user:profile'), {'token': token, 'data': data})
        r = c.get(reverse('user:profile'), {'token': token})
        data = json.loads(r.content.decode('utf8'))
        self.assertEqual(data['location'], [p1.id, None])

        # clear all
        data = json.dumps({'location': [None, None]})
        c.post(reverse('user:profile'), {'token': token, 'data': data})
        r = c.get(reverse('user:profile'), {'token': token})
        data = json.loads(r.content.decode('utf8'))
        self.assertEqual(data['location'], [None, None])

        # reset
        data = json.dumps({'location': [p1.id, c1.id]})
        c.post(reverse('user:profile'), {'token': token, 'data': data})

        # clear all
        data = json.dumps({'location': [None, None]})
        c.post(reverse('user:profile'), {'token': token, 'data': data})
        r = c.get(reverse('user:profile'), {'token': token})
        data = json.loads(r.content.decode('utf8'))
        self.assertEqual(data['location'], [None, None])

    def test_identification(self):
        # prepare data
        c = Client()
        user = create_user('1')
        token = user.token_info.token

        # should not be verified
        r = c.get(reverse('user:identification_verification'), {'token': token})
        r = json.loads(r.content.decode('utf8'))['is_verified']
        self.assertEqual(r, False)

        # update identification
        d = {'name': '某人', 'number': '111111111111111111'}
        r = c.post(reverse('user:identification'),
                   {'token': token, 'data': json.dumps(d)})
        self.assertEqual(r.status_code, 200)

        # get identification
        r = c.get(reverse('user:identification'), {'token': token})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['name'], '某人')
        self.assertEqual(r['number'], '111111111111111111')

        # should be verified
        user.identification.is_verified = True
        user.identification.save()
        r = c.get(reverse('user:identification_verification'), {'token': token})
        r = json.loads(r.content.decode('utf8'))['is_verified']
        self.assertEqual(r, True)

        # cannot update identification
        d = {'name': '某人', 'number': '111111111111111111'}
        r = c.post(reverse('user:identification'),
                   {'token': token, 'data': json.dumps(d)})
        self.assertEqual(r.status_code, 403)

    def test_student_identification(self):
        # prepare data
        c = Client()
        user = create_user('1')
        token = user.token_info.token

        # update identification
        d = {'school': '某校', 'number': '1234'}
        r = c.post(reverse('user:student_identification'),
                   {'token': token, 'data': json.dumps(d)})
        self.assertEqual(r.status_code, 200)

        # get identification
        r = c.get(reverse('user:student_identification'), {'token': token})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['school'], '某校')
        self.assertEqual(r['number'], '1234')
