import json
from datetime import datetime, date, timedelta
from django.core.urlresolvers import reverse
from django.test import Client, TestCase, TransactionTestCase
from main.models.location import Province, City
from main.models.user import User


class UserListTestCase(TestCase):
    def setUp(self):
        self.c = Client()

        time = datetime.now()
        user = User.create('0', name='user0', create_time=time)
        self.t = user.token.value
        for i in range(1, 20):
            time += timedelta(seconds=1)
            User.create(str(i), name='user' + str(i), create_time=time)

    def test_get_list_by_create_time_asc(self):
        r = self.c.get(reverse('user:root'),
                       {'token': self.t, 'limit': '20', 'order': '0'})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['name'], 'user0')

    def test_get_list_by_create_time_desc(self):
        r = self.c.get(reverse('user:root'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 20)
        self.assertEqual(r['list'][0]['name'], 'user19')

    def test_get_list_by_name_asc(self):
        r = self.c.get(reverse('user:root'),
                       {'token': self.t, 'limit': 20, 'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertLess(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_list_by_name_desc(self):
        r = self.c.get(reverse('user:root'),
                       {'token': self.t, 'limit': 20, 'order': 3})
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
        self.assertEqual(r, User.objects.get(
            phone_number='13010101010').token.value)

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
        self.c = Client()
        self.t = User.create('13010101010', 'password').token.value
        User.create('14010101010', username='godmother')

    def test_username_related(self):
        # get username when it's null
        r = self.c.get(reverse('self:username'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(r, None)

        # set a occupied username
        r = self.c.post(reverse('self:username'),
                        {'token': self.t, 'username': 'GodMother'})
        self.assertEqual(r.status_code, 403)

        # set a pure-digit username
        r = self.c.post(reverse('self:username'),
                        {'token': self.t, 'username': '1010101'})
        self.assertEqual(r.status_code, 400)

        # set a username containing invalid character
        r = self.c.post(reverse('self:username'),
                        {'token': self.t, 'username': 'GodFather!'})
        self.assertEqual(r.status_code, 400)

        # set a valid username
        r = self.c.post(reverse('self:username'),
                        {'token': self.t, 'username': 'GodFather'})
        self.assertEqual(r.status_code, 200)

        # get username now
        r = self.c.get(reverse('self:username'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))['username']
        self.assertEqual(r, 'godfather')

        # change username
        r = self.c.post(reverse('self:username'),
                        {'token': self.t, 'username': 'NotGodFather'})
        self.assertEqual(r.status_code, 403)

    def test_password_related(self):
        # password too short
        d = {'token': self.t,
             'new_password': 'short', 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 400)

        # password too long
        long = '11111111111111111111111'
        d = {'token': self.t,
             'new_password': long, 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 400)

        # reasonable password
        d = {'token': self.t,
             'new_password': 'andOpen', 'old_password': 'password'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 200)

        # validate new password
        user = User.objects.get(phone_number='13010101010')
        self.assertTrue(user.check_password('andOpen'))

        # invalid old password
        d = {'token': self.t,
             'new_password': 'wrong!', 'old_password': 'invalid'}
        r = self.c.post(reverse('self:password'), d)
        self.assertEqual(r.status_code, 403)


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.c = Client()

        self.u0 = User.create('0')
        self.u1 = User.create('1')
        self.t0 = self.u0.token.value
        self.t1 = self.u1.token.value

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
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        r = self.c.get(reverse('self:profile'), {'token': self.t0})
        r = json.loads(r.content.decode('utf8'))
        p = self.profile.copy()
        p['username'] = None
        p['icon'] = None
        p['create_time'] = self.u0.create_time.strftime('%Y-%m-%d')
        p['tags'] = ['test']
        self.assertEqual(r, p)

        r = self.c.get(reverse('user:profile', kwargs={'user_id': self.u0.id}),
                       {'token': self.t1})
        r = json.loads(r.content.decode('utf8'))
        p = self.profile.copy()
        p['username'] = None
        p['icon'] = None
        p['create_time'] = self.u0.create_time.strftime('%Y-%m-%d')
        p['tags'] = ['test']
        self.assertEqual(r, p)

    def test_tag_related(self):
        # with valid tag list
        d = json.dumps({'tags': ['T1', 'T2']})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        # with blank tag
        d = json.dumps({'tags': ['T1', 'T2', '  ']})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 400)

        # too many tags
        d = json.dumps({'tags': ['T1', 'T2', 'T3', 'T4', 'T5', 'T6']})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 400)

        # tag list should remain intact
        r = self.c.get(reverse('self:profile'), {'token': self.t0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['tags'], ['t1', 't2'])

    def test_location_related(self):
        # with both values
        d = json.dumps({'location': [self.p1.id, self.c1.id]})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        # clean location
        d = json.dumps({'location': [None, None]})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        # with province only
        d = json.dumps({'location': [self.p2.id, None]})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        # with invalid value
        d = json.dumps({'location': [self.p2.id, self.c1.id]})
        r = self.c.post(reverse('self:profile'), {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 400)

        # get location
        r = self.c.get(reverse('self:profile'), {'token': self.t0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['location'], [self.p2.id, None])


class UserIdentificationTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u0 = User.create('0')
        self.t0 = self.u0.token.value
        self.u1 = User.create('1')
        self.t1 = self.u1.token.value

    def test_post_and_get(self):
        d = json.dumps({'name': '测试',
                        'school': '蓝翔',
                        'id_number': '111111111111111111',
                        'student_id': '1234'})
        r = self.c.post(reverse('self:identification'),
                        {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 200)

        r = self.c.get(  # get own identification
            reverse('user:identification', kwargs={'user_id': self.u0.id}),
            {'token': self.t0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['name'], '测试')

        r = self.c.get(  # get other's identification
            reverse('user:identification', kwargs={'user_id': self.u0.id}),
            {'token': self.t1})
        r = json.loads(r.content.decode('utf8'))
        self.assertNotIn('id_number', r)

    def test_edit_verified_identification(self):
        self.u0.identification.is_verified = True
        self.u0.identification.save()
        d = json.dumps({'id_number': '222222222222222222'})
        r = self.c.post(reverse('self:identification'),
                        {'token': self.t0, 'data': d})
        self.assertEqual(r.status_code, 403)


class UserExperienceTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u = User.create('010')
        self.t = self.u.token.value

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
        r = self.c.get(reverse('self:education_experiences'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:education_experiences',
                               kwargs={'user_id': str(self.u.id)}),
                       {'token': self.t})
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['school'], 's1')

        r = self.c.get(reverse('self:fieldwork_experiences'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:fieldwork_experiences',
                               kwargs={'user_id': str(self.u.id)}),
                       {'token': self.t})
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['company'], 'c1')

        r = self.c.get(reverse('self:work_experiences'), {'token': self.t})
        r = json.loads(r.content.decode('utf8'))
        s = self.c.get(reverse('user:work_experiences',
                               kwargs={'user_id': str(self.u.id)}),
                       {'token': self.t})
        s = json.loads(s.content.decode('utf8'))
        self.assertEqual(r, s)
        self.assertEqual(r['list'][0]['begin_time'], '2003-09-01')

    def test_edit(self):
        d = json.dumps({'school': 's0', 'degree': 0, 'major': 'm0',
                        'begin_time': '2000-09-01',
                        'end_time': '2003-06-01'})
        self.c.post(
            reverse('self:education_experience',
                    kwargs={'exp_id': str(self.ee.id)}),
            {'token': self.t, 'data': d})
        self.assertEqual(self.u.education_experiences.all()[0].school, 's0')

        d = json.dumps({'company': 'c0',
                        'position': 'p0',
                        'description': 'd0',
                        'begin_time': '2000-09-01',
                        'end_time': None})
        self.c.post(
            reverse('self:fieldwork_experience',
                    kwargs={'exp_id': str(self.fe.id)}),
            {'token': self.t, 'data': d})
        self.assertEqual(
            self.u.fieldwork_experiences.all()[0].company, 'c0')

        d = json.dumps({'company': 'c0',
                        'position': 'p0',
                        'description': 'd0',
                        'begin_time': '2000-09-01',
                        'end_time': None})
        self.c.post(
            reverse('self:work_experience', kwargs={'exp_id': str(self.we.id)}),
            {'token': self.t, 'data': d})
        self.assertEqual(
            self.u.work_experiences.all()[0].company, 'c0')

    def test_delete_all(self):
        self.u.education_experiences.create(
            school='s2', degree=2, major='m2',
            begin_time=date(2001, 9, 1), end_time=date(2004, 6, 1)
        )
        self.c.delete(reverse('self:education_experiences'), 'token=' + self.t)
        self.assertEqual(self.u.education_experiences.count(), 0)

        self.u.fieldwork_experiences.create(
            company='c3', position='p3',
            description='d3',
            begin_time=date(2004, 3, 1),
        )
        self.c.delete(reverse('self:fieldwork_experiences'), 'token=' + self.t)
        self.assertEqual(self.u.fieldwork_experiences.count(), 0)

        self.u.work_experiences.create(
            company='c4', position='p4',
            description='d4',
            begin_time=date(2004, 9, 1),
        )
        self.c.delete(reverse('self:work_experiences'), 'token=' + self.t)
        self.assertEqual(self.u.work_experiences.count(), 0)

    def test_delete_single(self):
        self.u.education_experiences.create(
            school='s2', degree=2, major='m2',
            begin_time=date(2001, 9, 1), end_time=date(2004, 6, 1)
        )
        self.c.delete(reverse('self:education_experience',
                              kwargs={'exp_id': str(self.ee.id)}),
                      'token=' + self.t)
        self.assertEqual(self.u.education_experiences.count(), 1)
        self.assertEqual(self.u.education_experiences.all()[0].school, 's2')

        self.u.fieldwork_experiences.create(
            company='c3', position='p3',
            description='d3',
            begin_time=date(2004, 3, 1),
        )
        self.c.delete(reverse('self:fieldwork_experience',
                              kwargs={'exp_id': str(self.fe.id)}),
                      'token=' + self.t)
        self.assertEqual(self.u.fieldwork_experiences.count(), 1)
        self.assertEqual(self.u.fieldwork_experiences.all()[0].company, 'c3')

        self.u.work_experiences.create(
            company='c4', position='p4',
            description='d4',
            begin_time=date(2004, 9, 1),
        )
        self.c.delete(
            reverse('self:work_experience', kwargs={'exp_id': str(self.we.id)}),
            'token=' + self.t)
        self.assertEqual(self.u.work_experiences.count(), 1)
        self.assertEqual(self.u.work_experiences.all()[0].company, 'c4')


class UserFriendTestCase(TestCase):
    def setUp(self):
        self.c = Client()
        self.u0 = User.create('0')
        self.u1 = User.create('1')
        self.u2 = User.create('2')
        self.u0.friend_relations.create(friend=self.u1)
        self.u1.friend_relations.create(friend=self.u0)

    def test_disabled_friend(self):
        # if a user is disabled, he or she should not exist in friend list
        self.u1.is_enabled = False
        self.u1.save()
        r = self.c.get(reverse('self:friends'), {'token': self.u0.token.value})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)

    def test_check_friend_relation(self):
        r = self.c.get(
            reverse('self:friend', kwargs={'other_user_id': self.u1.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 200)
        r = self.c.get(
            reverse('self:friend', kwargs={'other_user_id': self.u2.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 404)

    def test_get_friend_list(self):
        self.u0.friend_relations.create(friend=self.u2)
        self.u2.friend_relations.create(friend=self.u0)
        r = self.c.get(reverse('self:friends'), {'token': self.u0.token.value})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreater(r['list'][0]['create_time'],
                           r['list'][-1]['create_time'])

    def test_get_friend_by_time_asc(self):
        self.u0.friend_relations.create(friend=self.u2)
        self.u2.friend_relations.create(friend=self.u0)
        r = self.c.get(reverse('self:friends'),
                       {'token': self.u0.token.value, 'order': 0})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLess(r['list'][0]['create_time'],
                        r['list'][-1]['create_time'])

    def test_get_friend_list_by_name_asc(self):
        self.u0.friend_relations.create(friend=self.u2)
        self.u2.friend_relations.create(friend=self.u0)
        r = self.c.get(reverse('self:friends'),
                       {'token': self.u0.token.value, 'order': 2})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertLessEqual(r['list'][0]['name'], r['list'][-1]['name'])

    def test_get_friend_list_by_name_desc(self):
        self.u0.friend_relations.create(friend=self.u2)
        self.u2.friend_relations.create(friend=self.u0)
        r = self.c.get(reverse('self:friends'),
                       {'token': self.u0.token.value, 'order': 3})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        self.assertGreaterEqual(r['list'][0]['name'], r['list'][-1]['name'])

    # 测试发送好友请求
    def test_send_friend_request(self):
        r = self.c.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u1.id}),
            {'token': self.u0.token.value})
        #已经加好友的不能进行请求
        self.assertEqual(r.status_code, 403)
        #判断好友关系

        r = self.c.get(reverse('user:friend',kwargs={'user_id':self.u0.id,'other_user_id':self.u1.id}),{'token':self.u0.token.value})
        self.assertEqual(r.status_code,200)
        r = self.c.get(reverse('user:friend',kwargs={'user_id':self.u0.id,'other_user_id':self.u2.id}),{'token':self.u0.token.value})
        self.assertEqual(r.status_code,404)

        r = self.c.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u2.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 200)

        #不能多次发送请求
        r = self.c.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u2.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 403)
        #不能向自己发送请求
        r = self.c.post(
            reverse('user:friend_requests', kwargs={'user_id': self.u0.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 400)

        r = self.c.get(
            reverse('self:friend_requests'),
            {'token': self.u2.token.value})
        r= json.loads(r.content.decode('utf8'))
        self.assertEqual(r['list'][0]['id'], self.u0.id)
        self.assertEqual(r['count'],0)
        #添加到好友
        r = self.c.post(reverse('self:friend',kwargs={'other_user_id':self.u0.id}),
            {'token': self.u2.token.value})
        self.assertEqual(r.status_code, 200)
        #已经是好友,添加到好友
        r = self.c.post(reverse('self:friend',kwargs={'other_user_id':self.u1.id}),
            {'token': self.u0.token.value})
        self.assertEqual(r.status_code, 403)
        #此时应该有两个好友
        r = self.c.get(reverse('self:friends'), {'token': self.u0.token.value})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 2)
        #删除好友
        r = self.c.delete(reverse('self:friend',kwargs={'other_user_id':self.u1.id}),
            'token=' + self.u0.token.value)
        self.assertEqual(r.status_code, 200)
        r = self.c.get(reverse('self:friends'), {'token': self.u0.token.value})
        r = json.loads(r.content.decode('utf8'))
        self.assertEqual(r['count'], 1)



    '''
    def test_get_visitors_list(self):
        r = self.c.get(reverse('self:visitors'),{'token',self.u0.token.value})
        self.assertEqual(r.status_code, 200)
        r = json.load(r.content.decode('utf8'))
        self.assertEqual(r['count'], 0)
    '''







