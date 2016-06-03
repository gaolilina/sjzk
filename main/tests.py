import hashlib
import json
import os
from datetime import datetime, date, timedelta

from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import Client, TestCase, TransactionTestCase

from ChuangYi import settings
from main.crypt import encrypt_phone_number
from main.models.location import Province, City, County
from main.models.team import Team
from main.models.team.need import TeamNeed
from main.models.team.task import TeamTask
from main.models.team.member import TeamMember
from main.models.team.achievement import TeamAchievement
from main.models.user import User

TEST_DATA = os.path.join(settings.BASE_DIR, 'test_data')


class UserListTestCase(TestCase):
    def setUp(self):
        time = datetime.now()
        user = User.enabled.create_user('0', name='user0', create_time=time)
        token = user.token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        for i in range(1, 20):
            time += timedelta(seconds=1)
            User.enabled.create_user(str(i), name='user' + str(i), create_time=time)

    def test_get_list_by_create_time_asc(self):
        r = self.c.get(reverse('user:root'),
                       {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'user0')

    def test_get_list_by_create_time_desc(self):
        r = self.c.get(reverse('user:root'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'user19')

    def test_get_list_by_name_asc(self):
        r = self.c.get(reverse('user:root'),
                       {'limit': 20, 'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertLess(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_list_by_name_desc(self):
        r = self.c.get(reverse('user:root'),
                       {'limit': 20, 'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertGreater(r['list'][0]['name'], r['list'][-1]['name'])


class UserRegisterTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        User.enabled.create_user('15010101010')

    def test_register(self):
        phone_number = encrypt_phone_number('13010101010')
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': 'password'})
        self.assertEqual(r.status_code, 200)
        r = json.loads(r.content.decode('utf8'))['token']
        c = Client(HTTP_USER_TOKEN=r)
        # check if token is usable
        r = c.get(reverse('self:icon'))
        self.assertEqual(r.status_code, 200)

    def test_register_with_invalid_password(self):
        phone_number = encrypt_phone_number('14010101010')
        password = '<6'
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': password})
        self.assertEqual(r.status_code, 400)
        password = '>20....................'
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': password})
        self.assertEqual(r.status_code, 400)

    def test_register_with_invalid_phone_number(self):
        phone_number = '12345678901234567890'
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': 'pass'})
        self.assertEqual(r.status_code, 400)

    def test_register_with_used_phone_number(self):
        phone_number = encrypt_phone_number('15010101010')
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': 'password'})
        self.assertEqual(r.status_code, 403)


class UserTokenTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        User.enabled.create_user('13010101010', 'SAPMan?', username='ohcrap')
        User.enabled.create_user('14010101010', 'OhNo!!', username='fb403', is_enabled=False)

    def test_get_token_by_phone_number(self):
        r = self.c.post(reverse('user:token'),
                        {'username': '13010101010', 'password': 'SAPMan?'})
        self.assertEqual(r.status_code, 200)

    def test_get_token_by_username(self):
        r = self.c.post(reverse('user:token'),
                        {'username': 'OhCrap', 'password': 'SAPMan?'})
        self.assertEqual(r.status_code, 200)

    def test_get_token_by_invalid_credential(self):
        r = self.c.post(reverse('user:token'),
                        {'username': 'oHcRap', 'password': 'ohcrap'})
        self.assertEqual(r.status_code, 401)

    def test_get_token_of_blocked_user(self):
        r = self.c.post(reverse('user:token'),
                        {'username': '14010101010', 'password': 'OhNo!!'})
        self.assertEqual(r.status_code, 403)

        r = self.c.post(reverse('user:token'),
                        {'username': 'FB403', 'password': 'OhNo!!'})
        self.assertEqual(r.status_code, 403)


class UserCredentialTestCase(TransactionTestCase):
    def setUp(self):
        token = User.enabled.create_user('13010101010', 'password').token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        User.enabled.create_user('14010101010', username='godmother')

    def test_username_related(self):
        # get username when it's null
        r = self.c.get(reverse('self:username'))
        r = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(r, None)

        # set a occupied username
        r = self.c.post(reverse('self:username'),
                        {'username': 'GodMother'})
        self.assertEqual(r.status_code, 403)

        # set a pure-digit username
        r = self.c.post(reverse('self:username'),
                        {'username': '1010101'})
        self.assertEqual(r.status_code, 400)

        # set a username containing invalid character
        r = self.c.post(reverse('self:username'),
                        {'username': 'GodFather!'})
        self.assertEqual(r.status_code, 400)

        # set a valid username
        r = self.c.post(reverse('self:username'),
                        {'username': 'GodFather'})
        self.assertEqual(r.status_code, 200)

        # get username now
        r = self.c.get(reverse('self:username'))
        r = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(r, 'godfather')

        # change username
        r = self.c.post(reverse('self:username'),
                        {'username': 'NotGodFather'})
        self.assertEqual(r.status_code, 403)

    def test_password_related(self):
        # password too short
        d = {'new_password': 'short', 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 400)

        # password too long
        long = '11111111111111111111111'
        d = {'new_password': long, 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 400)

        # reasonable password
        d = {'new_password': 'andOpen', 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 200)

        # validate new password
        user = User.objects.get(phone_number='13010101010')
        self.assertTrue(user.check_password('andOpen'))

        # invalid old password
        d = {'new_password': 'wrong!', 'old_password': 'invalid'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 403)


class UserIconTestCase(TestCase):
    def setUp(self):
        self.u = User.enabled.create_user('1')
        self.c = Client(HTTP_USER_TOKEN=self.u.token.value)

    def test(self):
        # no icon at the moment
        r = self.c.get(reverse('self:icon'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['icon_url'], None)
        # upload an icon
        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            r = self.c.post(reverse('self:icon'), {'icon': f})
        self.assertEqual(r.status_code, 200)
        # return an icon url
        r = self.c.get(reverse('self:icon'))
        r = json.loads(r.content.decode('utf8'))
        self.assertNotEqual(r['icon_url'], None)


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        t0 = self.u0.token.value
        self.c = Client(HTTP_USER_TOKEN=t0)

        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)
        self.ct1 = County.objects.create(name='ct1', city=self.c1)
        self.ct2 = County.objects.create(name='ct2', city=self.c1)

        self.profile = {
            'name': 'User 0',
            'description': 'testing...',
            'email': 'user0@example.com',
            'gender': 1,
            'birthday': '2000-10-24',
            'location': [self.p1.name, self.c1.name, self.ct1.name],
            'tags': ['Test'],
        }

    def test_get_profile(self):
        d = json.dumps(self.profile)
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['birthday'], '2000-10-24')

        r = self.c.get(reverse('user:profile', kwargs={'user_id': self.u0.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['email'], 'user0@example.com')

    def test_tag_related(self):
        # with valid tag list
        d = json.dumps({'tags': ['T1', 'T2', 'T3', 'T4']})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with blank tag
        d = json.dumps({'tags': ['T1', 'T2', '  ']})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 400)

        # too many tags
        d = json.dumps({'tags': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 400)

        # tag list should remain intact
        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], ['t1', 't2', 't3', 't4'])

        # set tags again
        d = json.dumps({'tags': ['T3', 'T4']})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)
        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], ['t3', 't4'])

        # clean tags
        d = json.dumps({'tags': []})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)
        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], [None])

    def test_location_related(self):
        # with both values
        d = json.dumps({'location': [self.p1.name, self.c1.name,
                                     self.ct1.name]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # clean location
        d = json.dumps({'location': [None, None, None]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with province only
        d = json.dumps({'location': [self.p2.name, None, None]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with invalid value
        d = json.dumps({'location': [None, self.c1.name,
                                     self.ct1.name]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 400)

        # get location
        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['location'], [self.p2.name, None, None])


class UserIdentificationTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.u1 = User.enabled.create_user('1')
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test_post_and_get(self):
        d = json.dumps({'name': '测试', 'id_number': '111111111111111111'})
        r = self.c0.post(reverse('self:identification'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # get own identification
        r = self.c0.get(
            reverse('user:identification', kwargs={'user_id': self.u0.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['name'], '测试')

        # get other's identification
        r = self.c1.get(
            reverse('user:identification', kwargs={'user_id': self.u0.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertNotIn('id_number', r)

    def test_edit_verified_identification(self):
        self.u0.identification.is_verified = True
        self.u0.identification.save()
        d = json.dumps({'id_number': '222222222222222222'})
        r = self.c0.post(reverse('self:identification'), {'data': d})
        self.assertEqual(r.status_code, 403)


class UserExperienceTestCase(TestCase):
    def setUp(self):
        self.u = User.enabled.create_user('010')
        self.c = Client(HTTP_USER_TOKEN=self.u.token.value)

        self.ee = self.u.education_experiences.create(
            school='s1', degree=1, major='m1',
            begin_time=date(2000, 9, 1), end_time=date(2003, 6, 1)
        )
        self.fe = self.u.fieldwork_experiences.create(
            company='c1', position='p1',
            description='d1',
            begin_time=date(2003, 3, 1), end_time=date(2003, 9, 1)
        )
        self.we = self.u.work_experiences.create(
            company='c1', position='p1',
            description='d1',
            begin_time=date(2003, 9, 1),
        )

    def test_get_all(self):
        r = self.c.get(reverse('self:education_experiences'))
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:education_experiences',
                               kwargs={'user_id': str(self.u.id)}))
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['school'], 's1')

        r = self.c.get(reverse('self:fieldwork_experiences'))
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:fieldwork_experiences',
                               kwargs={'user_id': str(self.u.id)}))
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['company'], 'c1')

        r = self.c.get(reverse('self:work_experiences'))
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:work_experiences',
                               kwargs={'user_id': str(self.u.id)}))
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['begin_time'], '2003-09-01')

    def test_edit(self):
        d = json.dumps({'school': 's0', 'degree': 0, 'major': 'm0',
                        'begin_time': '2000-09-01',
                        'end_time': '2003-06-01'})
        self.c.post(reverse('self:education_experience',
                            kwargs={'exp_id': str(self.ee.id)}), {'data': d})
        self.assertEqual(self.u.education_experiences.all()[0].school, 's0')

        d = json.dumps({'company': 'c0',
                        'position': 'p0',
                        'description': 'd0',
                        'begin_time': '2000-09-01',
                        'end_time': None})
        self.c.post(reverse('self:fieldwork_experience',
                            kwargs={'exp_id': str(self.fe.id)}), {'data': d})
        self.assertEqual(
            self.u.fieldwork_experiences.all()[0].company, 'c0')

        d = json.dumps({'company': 'c0',
                        'position': 'p0',
                        'description': 'd0',
                        'begin_time': '2000-09-01',
                        'end_time': None})
        self.c.post(reverse('self:work_experience',
                            kwargs={'exp_id': str(self.we.id)}), {'data': d})
        self.assertEqual(
            self.u.work_experiences.all()[0].company, 'c0')

    def test_delete_all(self):
        self.u.education_experiences.create(
            school='s2', degree=2, major='m2',
            begin_time=date(2001, 9, 1), end_time=date(2004, 6, 1)
        )
        self.c.delete(reverse('self:education_experiences'))
        self.assertEqual(self.u.education_experiences.count(), 0)

        self.u.fieldwork_experiences.create(
            company='c3', position='p3',
            description='d3',
            begin_time=date(2004, 3, 1),
        )
        self.c.delete(reverse('self:fieldwork_experiences'))
        self.assertEqual(self.u.fieldwork_experiences.count(), 0)

        self.u.work_experiences.create(
            company='c4', position='p4',
            description='d4',
            begin_time=date(2004, 9, 1),
        )
        self.c.delete(reverse('self:work_experiences'))
        self.assertEqual(self.u.work_experiences.count(), 0)

    def test_delete_single(self):
        self.u.education_experiences.create(
            school='s2', degree=2, major='m2',
            begin_time=date(2001, 9, 1), end_time=date(2004, 6, 1)
        )
        self.c.delete(reverse('self:education_experience',
                              kwargs={'exp_id': str(self.ee.id)}))
        self.assertEqual(self.u.education_experiences.count(), 1)
        self.assertEqual(self.u.education_experiences.all()[0].school, 's2')

        self.u.fieldwork_experiences.create(
            company='c3', position='p3',
            description='d3',
            begin_time=date(2004, 3, 1),
        )
        self.c.delete(reverse('self:fieldwork_experience',
                              kwargs={'exp_id': str(self.fe.id)}))
        self.assertEqual(self.u.fieldwork_experiences.count(), 1)
        self.assertEqual(self.u.fieldwork_experiences.all()[0].company, 'c3')

        self.u.work_experiences.create(
            company='c4', position='p4',
            description='d4',
            begin_time=date(2004, 9, 1),
        )
        self.c.delete(
            reverse('self:work_experience', kwargs={'exp_id': str(self.we.id)}))
        self.assertEqual(self.u.work_experiences.count(), 1)
        self.assertEqual(self.u.work_experiences.all()[0].company, 'c4')


class UserFriendTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.u2 = User.enabled.create_user('2')
        self.u0.friend_records.create(friend=self.u1)
        self.u1.friend_records.create(friend=self.u0)
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c2 = Client(HTTP_USER_TOKEN=self.u2.token.value)

    def test_disabled_friend(self):
        # if a user is disabled, he or she should not exist in friend list
        self.u1.is_enabled = False
        self.u1.save()
        r = self.c0.get(reverse('self:friends'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)

    def test_check_friend_relation(self):
        r = self.c0.get(
            reverse('self:friend', kwargs={'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(
            reverse('self:friend', kwargs={'other_user_id': self.u2.id}))
        self.assertEqual(r.status_code, 404)

    def test_get_friend_list(self):
        self.u0.friend_records.create(friend=self.u2)
        self.u2.friend_records.create(friend=self.u0)
        r = self.c0.get(reverse('self:friends'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreaterEqual(r['list'][0]['create_time'],
                                r['list'][-1]['create_time'])

    def test_get_friend_by_time_asc(self):
        self.u0.friend_records.create(friend=self.u2)
        self.u2.friend_records.create(friend=self.u0)
        r = self.c0.get(reverse('self:friends'), {'order': 0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLessEqual(r['list'][0]['create_time'],
                             r['list'][-1]['create_time'])

    def test_get_friend_list_by_name_asc(self):
        self.u0.friend_records.create(friend=self.u2)
        self.u2.friend_records.create(friend=self.u0)
        r = self.c0.get(reverse('self:friends'), {'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLessEqual(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_friend_list_by_name_desc(self):
        self.u0.friend_records.create(friend=self.u2)
        self.u2.friend_records.create(friend=self.u0)
        r = self.c0.get(reverse('self:friends'), {'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreaterEqual(r['list'][0]['name'], r['list'][-1]['name'])

    # 测试发送好友请求
    def test_send_friend_request(self):
        # 已经加好友的不能进行请求
        r = self.c0.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u1.id}))
        self.assertEqual(r.status_code, 403)

        # 判断好友关系
        r = self.c0.get(reverse('user:friend',
                                kwargs={'user_id': self.u0.id,
                                        'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('user:friend',
                                kwargs={'user_id': self.u0.id,
                                        'other_user_id': self.u2.id}))
        self.assertEqual(r.status_code, 404)

        r = self.c0.post(reverse('user:friend_requests',
                                 kwargs={'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)

        # 不能多次发送请求
        r = self.c0.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)
        # 不能向自己发送请求
        r = self.c0.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u0.id}))
        self.assertEqual(r.status_code, 400)

        r = self.c2.get(reverse('self:friend_requests'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.u0.id)
        self.assertEqual(r['count'], 0)
        # 添加到好友
        r = self.c2.post(
            reverse('self:friend', kwargs={'other_user_id': self.u0.id}))
        self.assertEqual(r.status_code, 200)
        # 已经是好友,添加到好友
        r = self.c0.post(
            reverse('self:friend', kwargs={'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 403)
        # 此时应该有两个好友
        r = self.c0.get(reverse('self:friends'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        # 删除好友
        r = self.c0.delete(
            reverse('self:friend', kwargs={'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('self:friends'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)


class UserVisitorTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test_visitors_request(self):
        r = self.c0.get(reverse('user:profile', kwargs={'user_id': self.u1.id}))
        self.assertEqual(r.status_code, 200)

        r = self.c1.get(reverse('self:visitors'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)


class UserLikersTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test_likers_request(self):
        #获取点赞者列表
        r = self.c1.get(reverse('self:likers'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)
        #判断是否点赞
        r = self.c0.get(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,400)
        #对用户进行点赞
        r = self.c0.post(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,200)
        #重复点赞
        r = self.c0.post(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,403)
        #判断是否点赞
        r = self.c0.get(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,200)
        #获取点赞者列表
        r = self.c1.get(reverse('self:likers'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)
        #取消点赞
        r = self.c0.delete(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,200)
        #重复取消点赞
        r = self.c0.delete(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,403)
        #获取点赞者列表
        r = self.c1.get(reverse('self:likers'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)
        #判断是否点赞
        r = self.c0.get(reverse('self:liked_user',kwargs={"user_id":self.u1.id}))
        self.assertEqual(r.status_code,400)


class UserFollowersTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test_followers_request(self):
        #获取粉丝列表
        r = self.c1.get(reverse('self:fans'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)
        #获取关注用户列表
        r = self.c0.get(reverse('self:followed_users'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)
        #判断u0是否为u1的粉丝
        r = self.c1.get(reverse('self:fan',kwargs={'other_user_id':self.u0.id}))
        self.assertEqual(r.status_code, 404)
        #关注某人
        r = self.c0.post(reverse('self:followed_user',kwargs={'other_user_id':self.u1.id}))
        self.assertEqual(r.status_code, 200)
        #重复关注某人
        r = self.c0.post(reverse('self:followed_user',kwargs={'other_user_id':self.u1.id}))
        self.assertEqual(r.status_code, 403)
        #判断u0是否为u1的粉丝
        r = self.c1.get(reverse('self:fan',kwargs={'other_user_id':self.u0.id}))
        self.assertEqual(r.status_code, 200)
        #获取粉丝列表
        r = self.c1.get(reverse('self:fans'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)
        #获取关注用户列表
        r = self.c0.get(reverse('self:followed_users'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)


class TeamListTestCase(TestCase):
    def setUp(self):
        time = datetime.now()
        self.user = User.enabled.create_user('0', name='user0', create_time=time)
        token = self.user.token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        for i in range(1, 21):
            Team.create(self.user, 'team' + str(i))

    def test_create(self):
        # 测试新建团队
        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)
        self.ct1 = County.objects.create(name='ct1', city=self.c1)
        self.ct2 = County.objects.create(name='ct2', city=self.c1)

        d = json.dumps({'name': 'team1',
                        'description': 'Team Test!',
                        'url': 'http://www.baidu.com',
                        'location': [self.p1.name, self.c1.name, self.ct1.name],
                        'fields': ['field1', 'field2'],
                        'tags': ['tag1', 'tag2']})
        r = self.c.post(reverse('team:team_create'), {'data': d})
        self.assertEqual(r.status_code, 200)

    def test_get_own_list(self):
        # 测试获取用户创建的团队
        self.user1 = User.enabled.create_user('1', name='user1',
                                              create_time=datetime.now())
        token1 = self.user1.token.value
        self.c1 = Client(HTTP_USER_TOKEN=token1)
        for i in range(1, 21):
            Team.create(self.user1, 'own_team' + str(i))

        r = self.c1.get(reverse('team:teams_owned'),
                        {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'own_team1')

    def test_get_member_list(self):
        # 测试获取用户参加的团队
        self.user1 = User.enabled.create_user('1', name='user1',
                                              create_time=datetime.now())
        token1 = self.user1.token.value
        self.c1 = Client(HTTP_USER_TOKEN=token1)
        for i in range(1, 11):
            Team.create(self.user1, 'user1_team' + str(i))

        self.user2 = User.enabled.create_user('2', name='user2',
                                              create_time=datetime.now())
        token2 = self.user2.token.value
        self.c2 = Client(HTTP_USER_TOKEN=token2)
        for i in range(1, 11):
            team = Team.create(self.user2, 'user2_team' + str(i))
            team_member = TeamMember(team=team, member=self.user1)
            team_member.save()

        r = self.c1.get(reverse('team:teams_joined'),
                        {'limit': '20', 'order': '0', 'is_owner': False})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 10)
        self.assertEqual(r['list'][0]['name'], 'user2_team1')

    def test_get_list_by_create_time_asc(self):
        r = self.c.get(reverse('team:teams'),
                       {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'team1')

    def test_get_list_by_create_time_desc(self):
        r = self.c.get(reverse('team:teams'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'team20')

    def test_get_list_by_name_asc(self):
        r = self.c.get(reverse('team:teams'),
                       {'limit': 20, 'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertLess(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_list_by_name_desc(self):
        r = self.c.get(reverse('team:teams'),
                       {'limit': 20, 'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertGreater(r['list'][0]['name'], r['list'][-1]['name'])


class TeamProfileTestCase(TestCase):
    def setUp(self):
        self.u = User.enabled.create_user('0')
        self.t = Team.create(self.u, 'test')

        self.c = Client(HTTP_USER_TOKEN=self.u.token.value)

        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)
        self.ct1 = County.objects.create(name='ct1', city=self.c1)
        self.ct2 = County.objects.create(name='ct2', city=self.c1)

        self.profile = {'name': 'team1',
                        'description': 'Team Test!',
                        'url': 'http://www.baidu.com',
                        'location': [self.p1.name, self.c1.name, self.ct1.name],
                        'fields': ['field1', 'field2'],
                        'is_recruiting': True,
                        'tags': ['tag1', 'tag2']}

    def test_create(self):
        d = json.dumps({'name': 'team100'})
        r = self.c.post(reverse('team:team_create'), {'data': d})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['team_id'], 2)

    def test_set_and_get_profile(self):
        d = json.dumps(self.profile)
        self.c.post(reverse('team:profile',
                            kwargs={'team_id': self.t.id}), {'data': d})

        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        p = self.profile.copy()
        p['id'] = self.t.id
        p['owner_id'] = self.u.id
        p['icon_url'] = None
        p['is_recruiting'] = True
        p['liker_count'] = 0
        p['fan_count'] = 0
        p['visitor_count'] = 0
        p['create_time'] = self.t.create_time.isoformat()[:-3]
        self.assertEqual(r, p)

    def test_tag_related(self):
        # with valid tag list
        d = json.dumps({'tags': ['T1', 'T2']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEquals(r.status_code, 200)

        # with blank tag
        d = json.dumps({'tags': ['T1', 'T2', '  ']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # too many tags
        d = json.dumps({'tags': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # tag list should remain intact
        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], ['t1', 't2'])

        # set tags again
        d = json.dumps({'tags': ['L1', 'L2']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEquals(r.status_code, 200)
        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], ['l1', 'l2'])

    def test_fields_related(self):
        # with valid tag list
        d = json.dumps({'fields': ['F1', 'F2']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})

        # with blank tag
        d = json.dumps({'fields': ['F1', 'F2', '  ']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # too many tags
        d = json.dumps({'fields': ['F1', 'F2', 'F3']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # tag list should remain intact
        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['fields'], ['f1', 'f2'])

    def test_location_related(self):
        # with both values
        d = json.dumps({'location': [self.p1.name, self.c1.name,
                                     self.ct1.name]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with string values
        d = json.dumps({'location': ['北京', '北京', '海淀']})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # clean location
        d = json.dumps({'location': [None, None, None]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with province only
        d = json.dumps({'location': [self.p2.name, None, None]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with invalid value
        d = json.dumps({'location': [None, self.c1.name,
                                     self.ct1.name]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # get location
        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['location'], [self.p2.name, None, None])


class TeamIconTestCase(TestCase):
    def setUp(self):
        self.u = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.t = Team.create(self.u, 'test')
        self.c = Client(HTTP_USER_TOKEN=self.u.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test(self):
        # no icon at the moment
        r = self.c.get(reverse('team:icon', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['icon_url'], None)
        # upload an icon
        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            r = self.c.post(reverse('team:icon',
                                    kwargs={'team_id': self.t.id}), {'icon': f})
        r = json.loads(r.content.decode('utf8'))
        self.assertNotEqual(r['icon_url'], None)
        # upload limit
        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            r = self.c1.post(reverse('team:icon',
                                     kwargs={'team_id': self.t.id}), {'icon': f})
        self.assertEqual(r.status_code, 400)
        # return an icon url
        r = self.c.get(reverse('team:icon', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertNotEqual(r['icon_url'], None)


class TeamMemberTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.u2 = User.enabled.create_user('2')
        self.t = Team.create(self.u0, 'test')

        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)
        self.c2 = Client(HTTP_USER_TOKEN=self.u2.token.value)

        self.t.member_records.create(member=self.u1)

    def test_disabled_member(self):
        # if a user is disabled, he or she should not exist in member list
        self.u1.is_enabled = False
        self.u1.save()
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)

    def test_check_member_relation(self):
        r = self.c0.get(reverse('team:member', kwargs={'team_id': self.t.id}),
                        {'user_id': self.u1.id})
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:member', kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 404)
        r = self.c0.get(reverse('team:member', kwargs={'team_id': self.t.id}),
                        {'user_id':self.u2.id})
        self.assertEqual(r.status_code, 404)

    def test_get_member_list(self):
        self.t.member_records.create(member=self.u2)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreaterEqual(r['list'][0]['create_time'],
                                r['list'][-1]['create_time'])

    def test_get_member_by_time_asc(self):
        self.t.member_records.create(member=self.u2)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}),
                        {'order': 0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLessEqual(r['list'][0]['create_time'],
                             r['list'][-1]['create_time'])

    def test_get_member_list_by_name_asc(self):
        self.t.member_records.create(member=self.u2)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}),
                        {'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLessEqual(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_member_list_by_name_desc(self):
        self.t.member_records.create(member=self.u2)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}),
                        {'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreaterEqual(r['list'][0]['name'], r['list'][-1]['name'])

    # 测试发送加入团队申请
    def test_send_member_request(self):
        # 已经是成员的不能进行申请
        r = self.c1.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 403)
        # 创始人不能发送申请
        r = self.c0.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 400)
        # 对方已经发送了加入团队邀请
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 403)
        # 发送加入团队请求
        r = self.c2.delete(reverse('team:invitation_self',
                                   kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        # 不能多次发送申请
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 403)

        # 获取申请列表
        r = self.c0.get(reverse('team:member_requests',
                                kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.u2.id)
        self.assertEqual(r['count'], 0)
        # 成员不能拉取申请列表
        r = self.c1.get(reverse('team:member_requests',
                                kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 404)
        # 添加成员
        r = self.c0.post(reverse('team:memberSelf', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        # 已经是成员,不能添加成员
        r = self.c0.post(reverse('team:memberSelf', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)
        # 此时应该有两个成员
        r = self.c0.get(reverse('team:members',
                                kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        # 删除成员
        r = self.c0.delete(reverse('team:memberSelf', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)

        # 忽略加入团队请求
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.delete(reverse('team:member_request', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:member_requests',
                                kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.u2.id)

    # 测试发送加入团队邀请
    def test_send_member_invitation(self):
        # 已经是成员的不能进行邀请
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u1.id}))
        self.assertEqual(r.status_code, 403)
        # 除团队创始人其他人不能发送邀请
        r = self.c1.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)
        # 对方已经发送了加入团队申请
        r = self.c2.post(reverse('team:member_requests',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)
        # 发送加入团队邀请
        r = self.c0.delete(reverse('team:member_request', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        # 不能多次发送邀请
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)

        # 获取邀请列表
        r = self.c2.get(reverse('team:invitations'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.t.id)
        self.assertEqual(r['count'], 0)
        # 同意邀请
        r = self.c2.post(reverse('team:invitation_self',
                                 kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        # 此时应该有两个成员
        r = self.c0.get(reverse('team:members',
                                kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        # 删除成员
        r = self.c0.delete(reverse('team:memberSelf', kwargs={
            'team_id': self.t.id,
            'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:members', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)

        # 忽略加入团队邀请
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c2.delete(reverse('team:invitation_self',
                                   kwargs={'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.post(reverse('team:invitation',
                                 kwargs={'team_id': self.t.id,
                                         'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c2.get(reverse('team:invitations'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.t.id)


class TeamNeedTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.t0 = Team.create(self.u0, 'test0')
        self.t1 = Team.create(self.u1, 'test1')

        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

        for i in range(1, 11):
            need = TeamNeed(team=self.t0, description='Need' + str(i),
                            create_time=datetime.now())
            need.save()
        for i in range(11, 21):
            need = TeamNeed(team=self.t1, description='Need' + str(i),
                            create_time=datetime.now())
            need.save()

    def test_create(self):
        # 测试发布需求
        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)
        self.ct1 = County.objects.create(name='ct1', city=self.c1)
        self.ct2 = County.objects.create(name='ct2', city=self.c1)

        d = json.dumps({'description': 'Team Need Test!',
                        'number': 10,
                        'gender': 0,
                        'location': [self.p1.name, self.c1.name,
                                     self.ct1.name]})
        r = self.c0.post(
                reverse('team:team_needs', kwargs={'team_id': self.t0.id}),
                {'data': d})
        self.assertEqual(r.status_code, 200)

    def test_get_one_team_list(self):
        # 测试获取某一团队的需求
        r = self.c0.get(
                reverse('team:team_needs', kwargs={'team_id': self.t0.id}),
                {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['description'], 'Need1')

    def test_get_list_by_create_time_asc(self):
        r = self.c0.get(
                reverse('team:needs'), {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['description'], 'Need1')

    def test_get_list_by_create_time_desc(self):
        r = self.c0.get(reverse('team:needs'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['description'], 'Need20')

    def test_delete(self):
        # 只能团队创始人删除
        r = self.c1.delete(
                reverse('team:need_delete', kwargs={'team_id': self.t0.id,
                                                    'need_id': 1}))
        self.assertEqual(r.status_code, 403)
        # 需求不属于此团队
        r = self.c1.delete(
                reverse('team:need_delete', kwargs={'team_id': self.t1.id,
                                                    'need_id': 1}))
        self.assertEqual(r.status_code, 400)
        # 测试删除需求
        r = self.c0.delete(
                reverse('team:need_delete', kwargs={'team_id': self.t0.id,
                                                    'need_id': 1}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:needs'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 19)


class TeamTaskTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.u2 = User.enabled.create_user('2')
        self.u3 = User.enabled.create_user('3')
        self.t0 = Team.create(self.u0, 'test0')

        self.t0.member_records.create(member=self.u1)
        self.t0.member_records.create(member=self.u2)

        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)
        self.c2 = Client(HTTP_USER_TOKEN=self.u2.token.value)
        self.c3 = Client(HTTP_USER_TOKEN=self.u3.token.value)

        time = datetime.now()
        for i in range(1, 21):
            time += timedelta(seconds=1)
            task = TeamTask(team=self.t0, name='task' + str(i),
                            description='Test', create_time=time)
            task.save()
            task.executors.add(self.u1, self.u2)

    def test_create(self):
        # 测试发布任务
        d = json.dumps({'name': 'Task0',
                        'description': 'Team Task Test!',
                        'executors_id': [2, 3]})
        r = self.c0.post(
                reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                {'data': d})
        r = json.loads(r.content.decode('utf8'))
        self.assertNotEqual(r['task_id'], None)
        # 只有创始人能发布任务
        d = json.dumps({'name': 'Task0',
                        'description': 'Team Task Test!',
                        'executors_id': [2, 3]})
        r = self.c1.post(
                reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                {'data': d})
        self.assertEqual(r.status_code, 403)
        # 只能给团队成员发布任务
        d = json.dumps({'name': 'Task0',
                        'description': 'Team Task Test!',
                        'executors_id': [2, 3, 4]})
        r = self.c0.post(
                reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                {'data': d})
        self.assertEqual(r.status_code, 403)

    def test_get_own_list(self):
        # 测试获取用户收到的所有任务
        r = self.c1.get(
                reverse('team:tasks_self'), {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'task1')

    def test_get_one_team_list(self):
        # 测试获取某一团队的所有任务
        r = self.c0.get(
                reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'task1')

    def test_get_list_by_create_time_asc(self):
        r = self.c0.get(
                reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'task1')

    def test_get_list_by_create_time_desc(self):
        r = self.c0.get(reverse('team:tasks', kwargs={'team_id': self.t0.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'task20')

    def test_get_member_list_by_name_asc(self):
        r = self.c0.get(reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                        {'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertLessEqual(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_member_list_by_name_desc(self):
        r = self.c0.get(reverse('team:tasks', kwargs={'team_id': self.t0.id}),
                        {'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertGreaterEqual(r['list'][0]['name'], r['list'][-1]['name'])

    def test_mark_finish(self):
        # 非执行者不能标记任务完成
        r = self.c3.post(
                reverse('team:task_marker', kwargs={'team_id': self.t0.id,
                                                    'task_id': 1}))
        self.assertEqual(r.status_code, 403)
        # 用户标记为已完成
        r = self.c1.post(
                reverse('team:task_marker', kwargs={'team_id': self.t0.id,
                                                    'task_id': 1}))
        self.assertEqual(r.status_code, 200)
        # 用户未标记完成
        r = self.c0.post(
                reverse('team:task', kwargs={'team_id': self.t0.id,
                                             'task_id': 1}))
        self.assertEqual(r.status_code, 400)
        # 所有用户标记完成，创始人确认
        r = self.c2.post(
                reverse('team:task_marker', kwargs={'team_id': self.t0.id,
                                                    'task_id': 1}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.post(
                reverse('team:task', kwargs={'team_id': self.t0.id,
                                             'task_id': 1}))
        self.assertEqual(r.status_code, 200)


class TeamAchievementTestCase(TestCase):
    def setUp(self):
        self.u0 = User.enabled.create_user('0')
        self.u1 = User.enabled.create_user('1')
        self.t0 = Team.create(self.u0, 'test0')
        self.t1 = Team.create(self.u1, 'test1')

        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)
        t = datetime.now()

        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            file = SimpleUploadedFile('', b'')
            with Image.open(f) as image:
                image.save(file, 'JPEG')
            md5 = hashlib.md5()
            md5.update(datetime.now().isoformat().encode())
            file.name = md5.hexdigest() + '.jpg'
            for i in range(1, 11):
                t += timedelta(seconds=1)
                a = TeamAchievement(team=self.t0,
                                    description='Achievement'+str(i),
                                    create_time=t)
                a.picture = file
                a.save()
            for i in range(11, 21):
                t += timedelta(seconds=1)
                a = TeamAchievement(team=self.t1,
                                    description='Achievement'+str(i),
                                    create_time=t)
                a.picture = file
                a.save()
                image.close()
                f.close()

    def test_create(self):
        # 测试发布成果
        description = 'Team Achievement Test!'
        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            r = self.c0.post(reverse('team:team_achievements',
                                     kwargs={'team_id': self.t0.id}),
                             {'description': description, 'picture': f})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['achievement_id'], 21)

    def test_get_one_team_list(self):
        # 测试获取某一团队的成果
        r = self.c0.get(
                reverse('team:team_achievements',
                        kwargs={'team_id': self.t0.id}),
                {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 10)
        self.assertEqual(r['list'][0]['description'], 'Achievement1')
        self.assertNotEqual(r['list'][0]['picture_url'], None)

    def test_get_list(self):
        # 测试获取所有团队的成果
        r = self.c0.get(reverse('team:achievements'),
                        {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['description'], 'Achievement1')

    def test_get_list_by_create_time_desc(self):
        r = self.c0.get(reverse('team:achievements'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['description'], 'Achievement20')

    def test_delete(self):
        # 只能团队创始人删除
        r = self.c1.delete(
                reverse('team:achievement_delete',
                        kwargs={'team_id': self.t0.id,
                                'achievement_id': 1}))
        self.assertEqual(r.status_code, 403)
        # 需求不属于此团队
        r = self.c1.delete(
                reverse('team:achievement_delete',
                        kwargs={'team_id': self.t1.id,
                                'achievement_id': 1}))
        self.assertEqual(r.status_code, 400)
        # 测试删除需求
        r = self.c0.delete(
                reverse('team:achievement_delete',
                        kwargs={'team_id': self.t0.id,
                                'achievement_id': 1}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:achievements'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 19)

