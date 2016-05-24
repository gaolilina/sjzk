import json
import os
from datetime import datetime, date, timedelta

from django.core.urlresolvers import reverse
from django.test import Client, TestCase, TransactionTestCase

from ChuangYi import settings
from main.models.location import Province, City
from main.models.team import Team
from main.models.user import User

TEST_DATA = os.path.join(settings.BASE_DIR, 'test_data')

'''
class UserListTestCase(TestCase):
    def setUp(self):
        time = datetime.now()
        user = User.create('0', name='user0', create_time=time)
        token = user.token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        for i in range(1, 20):
            time += timedelta(seconds=1)
            User.create(str(i), name='user' + str(i), create_time=time)

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
        User.create('15010101010')

    def test_register(self):
        phone_number = User.encrypt_phone_number('13010101010')
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': 'password'})
        self.assertEqual(r.status_code, 200)
        r = json.loads(r.content.decode('utf8'))['token']
        c = Client(HTTP_USER_TOKEN=r)
        # check if token is usable
        r = c.get(reverse('self:icon'))
        self.assertEqual(r.status_code, 200)

    def test_register_with_invalid_password(self):
        phone_number = User.encrypt_phone_number('14010101010')
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
        phone_number = User.encrypt_phone_number('15010101010')
        r = self.c.post(reverse('user:root'),
                        {'phone_number': phone_number, 'password': 'password'})
        self.assertEqual(r.status_code, 403)


class UserTokenTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        User.create('13010101010', 'SAPMan?', username='ohcrap')
        User.create('14010101010', 'OhNo!!', username='fb403', is_enabled=False)

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
        token = User.create('13010101010', 'password').token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        User.create('14010101010', username='godmother')

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
        self.u = User.create('1')
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
        self.u0 = User.create('0')
        t0 = self.u0.token.value
        self.c = Client(HTTP_USER_TOKEN=t0)

        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)

        self.profile = {
            'name': 'User 0',
            'description': 'testing...',
            'email': 'user0@example.com',
            'gender': 1,
            'birthday': '2000-10-24',
            'location': [self.p1.id, self.c1.id],
            'tags': ['Test'],
        }

    def test_get_profile(self):
        d = json.dumps(self.profile)
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        p = self.profile.copy()
        p['id'] = self.u0.id
        p['username'] = None
        p['icon'] = None
        p['create_time'] = self.u0.create_time.isoformat()[:-3]
        p['tags'] = ['test']
        self.assertEqual(r, p)

        r = self.c.get(reverse('user:profile', kwargs={'user_id': self.u0.id}))
        r = json.loads(r.content.decode('utf8'))
        p = self.profile.copy()
        p['id'] = self.u0.id
        p['username'] = None
        p['icon'] = None
        p['create_time'] = self.u0.create_time.isoformat()[:-3]
        p['tags'] = ['test']
        self.assertEqual(r, p)

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
        self.assertEqual(r['tags'], [])

    def test_location_related(self):
        # with both values
        d = json.dumps({'location': [self.p1.id, self.c1.id]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # clean location
        d = json.dumps({'location': [None, None]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with province only
        d = json.dumps({'location': [self.p2.id, None]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with invalid value
        d = json.dumps({'location': [self.p2.id, self.c1.id]})
        r = self.c.post(reverse('self:profile'), {'data': d})
        self.assertEqual(r.status_code, 400)

        # get location
        r = self.c.get(reverse('self:profile'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['location'], [self.p2.id, None])


class UserIdentificationTestCase(TestCase):
    def setUp(self):
        self.u0 = User.create('0')
        self.c0 = Client(HTTP_USER_TOKEN=self.u0.token.value)
        self.u1 = User.create('1')
        self.c1 = Client(HTTP_USER_TOKEN=self.u1.token.value)

    def test_post_and_get(self):
        d = json.dumps({'name': '测试',
                        'school': '蓝翔',
                        'id_number': '111111111111111111',
                        'student_id': '1234'})
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
        self.u = User.create('010')
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
        self.u0 = User.create('0')
        self.u1 = User.create('1')
        self.u2 = User.create('2')
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
        self.u0 = User.create('0')
        self.u1 = User.create('1')
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
        self.u0 = User.create('0')
        self.u1 = User.create('1')
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
        self.u0 = User.create('0')
        self.u1 = User.create('1')
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
        self.user = User.create('0', name='user0', create_time=time)
        token = self.user.token.value
        self.c = Client(HTTP_USER_TOKEN=token)
        for i in range(1, 21):
            Team.create(self.user, 'team' + str(i))

    def test_create(self):
        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)

        d = json.dumps({'name': 'team1',
                        'description': 'Team Test!',
                        'url': 'http://www.baidu.com',
                        'location': [self.p1.id, self.c1.id],
                        'fields': ['field1', 'field2'],
                        'tags': ['tag1', 'tag2']})
        r = self.c.post(reverse('team:rootSelf'), {'data': d})
        self.assertEqual(r.status_code, 200)

    def test_get_own_list(self):
        self.user1 = User.create('1', name='user1', create_time=datetime.now())
        token1 = self.user1.token.value
        self.c1 = Client(HTTP_USER_TOKEN=token1)
        for i in range(1, 21):
            Team.create(self.user1, 'own_team' + str(i))

        r = self.c1.get(reverse('team:rootSelf'),
                       {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'own_team1')

    def test_get_list_by_create_time_asc(self):
        r = self.c.get(reverse('team:root'),
                       {'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'team1')

    def test_get_list_by_create_time_desc(self):
        r = self.c.get(reverse('team:root'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'team20')

    def test_get_list_by_name_asc(self):
        r = self.c.get(reverse('team:root'),
                       {'limit': 20, 'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertLess(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_list_by_name_desc(self):
        r = self.c.get(reverse('team:root'),
                       {'limit': 20, 'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertGreater(r['list'][0]['name'], r['list'][-1]['name'])


class TeamProfileTestCase(TestCase):
    def setUp(self):
        self.u = User.create('0')
        self.t = Team.create(self.u, 'test')

        self.c = Client(HTTP_USER_TOKEN=self.u.token.value)

        self.p1 = Province.objects.create(name='p1')
        self.p2 = Province.objects.create(name='p2')
        self.c1 = City.objects.create(name='c1', province=self.p1)
        self.c2 = City.objects.create(name='c2', province=self.p1)

        self.profile = {'name': 'team1',
                        'description': 'Team Test!',
                        'url': 'http://www.baidu.com',
                        'location': [self.p1.id, self.c1.id],
                        'fields': ['field1', 'field2'],
                        'is_recruiting': True,
                        'tags': ['tag1', 'tag2']}

    def test_create(self):
        d = json.dumps({'name': 'team100'})
        r = self.c.post(reverse('team:rootSelf'), {'data': d})
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

        p['owner_id'] = self.u.id
        p['icon'] = None
        p['is_recruiting'] = True
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
        d = json.dumps({'location': [self.p1.id, self.c1.id]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # clean location
        d = json.dumps({'location': [None, None]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with province only
        d = json.dumps({'location': [self.p2.id, None]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 200)

        # with invalid value
        d = json.dumps({'location': [self.p2.id, self.c1.id]})
        r = self.c.post(reverse('team:profile',
                                kwargs={'team_id': self.t.id}), {'data': d})
        self.assertEqual(r.status_code, 400)

        # get location
        r = self.c.get(reverse('team:profile',
                               kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['location'], [self.p2.id, None])


class TeamIconTestCase(TestCase):
    def setUp(self):
        self.u = User.create('0')
        self.u1 = User.create('1')
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
        self.assertEqual(r.status_code, 200)
        # upload limit
        with open(os.path.join(TEST_DATA, 'kim.png'), 'rb') as f:
            r = self.c1.post(reverse('team:icon',
                                     kwargs={'team_id': self.t.id}), {'icon': f})
        self.assertEqual(r.status_code, 400)
        # return an icon url
        r = self.c.get(reverse('team:icon', kwargs={'team_id': self.t.id}))
        r = json.loads(r.content.decode('utf8'))
        self.assertNotEqual(r['icon_url'], None)
'''


class TeamMemberTestCase(TestCase):
    def setUp(self):
        self.u0 = User.create('0')
        self.u1 = User.create('1')
        self.u2 = User.create('2')
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
'''
    # 测试发送加入团队申请
    def test_send_member_request(self):
        # 已经是成员的不能进行申请
        r = self.c0.post(
            reverse('team:member_requests', kwargs={'team_id': self.t.id,
                                                    'user_id': self.u1.id}))
        self.assertEqual(r.status_code, 403)

        # 判断成员关系
        r = self.c0.get(reverse('team:member', kwargs={'user_id': self.u0.id,
                                                       'team_id': self.t.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:member',
                                kwargs={'user_id': self.u0.id,
                                        'other_user_id': self.u2.id}))
        self.assertEqual(r.status_code, 404)

        r = self.c0.post(reverse('team:member_requests',
                                 kwargs={'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 200)

        # 不能多次发送申请
        r = self.c0.post(
            reverse('team:member_requests', kwargs={'user_id': self.u2.id}))
        self.assertEqual(r.status_code, 403)
        # 不能向创始人发送申请
        r = self.c0.post(
            reverse('team:member_requests', kwargs={'user_id': self.u0.id}))
        self.assertEqual(r.status_code, 400)

        r = self.c2.get(reverse('team:member_requests'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.u0.id)
        self.assertEqual(r['count'], 0)
        # 添加成员
        r = self.c2.post(
            reverse('team:member', kwargs={'other_user_id': self.u0.id}))
        self.assertEqual(r.status_code, 200)
        # 已经是成员,添加成员
        r = self.c0.post(
            reverse('team:member', kwargs={'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 403)
        # 此时应该有两个成员
        r = self.c0.get(reverse('team:members'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        # 删除成员
        r = self.c0.delete(
            reverse('team:member', kwargs={'other_user_id': self.u1.id}))
        self.assertEqual(r.status_code, 200)
        r = self.c0.get(reverse('team:members'))
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)
'''
