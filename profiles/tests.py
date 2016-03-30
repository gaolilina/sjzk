import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from location.models import City, Province
from user.tests import create_user


class UserProfileTestCase(TestCase):
    def test_set_and_get_profile(self):
        # prepare test data
        user = create_user('11111111111', '111111111111111')
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

        client = Client()

        # set profile
        response = client.post(reverse('user:profile:root'),
                               {'token': token, 'data': data})
        self.assertEqual(response.status_code, 200)

        # get profile
        response = client.get(reverse('user:profile:root'), {'token': token})
        self.assertEqual(response.status_code, 200)
        r = json.loads(response.content.decode('utf8'))
        self.assertEqual(r['name'], '龙裔')
        self.assertEqual(r['description'], 'Fus Ro Dah!')
        self.assertEqual(r['email'], 'dragonborn@skyrim')
        self.assertEqual(r['gender'], 1)
        self.assertEqual(r['birthday'], '1990-01-01')
        self.assertEqual(r['location'], [province.id, city.id])
        self.assertEqual(r['tags'], ['Nord', 'Warrior', 'Two-handed'])

        user_id = user.id
        # now try get and set profile above from another user
        user = create_user('21111111111', '211111111111111')
        token = user.token_info.token
        response = client.get(
            reverse('user:profile:id', kwargs={'user_id': user_id}),
            {'token': token},
        )
        self.assertEqual(response.status_code, 200)

        data = json.dumps({'name': '抓根宝'})
        response = client.post(
            reverse('user:profile:id', kwargs={'user_id': user_id}),
            {'token': token, 'data': data},
        )
        self.assertEqual(response.status_code, 403)

    def test_tag(self):
        # prepare user
        user = create_user('1', '1')
        token = user.token_info.token

        client = Client()
        # get tag for first time
        response = client.get(reverse('user:profile:root'), {'token': token})
        tags = json.loads(response.content.decode('utf8'))['tags']
        self.assertEqual(tags, [])

        # set 5 tags
        data = json.dumps({'tags': ['t1', 't2', 't3', 't4', 't5']})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})

        # then set 2 tags
        data = json.dumps({'tags': ['t6', 't3']})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})
        response = client.get(reverse('user:profile:root'), {'token': token})
        tags = json.loads(response.content.decode('utf8'))['tags']
        self.assertEqual(tags, ['t6', 't3'])

        # then clear all tags
        data = json.dumps({'tags': []})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})
        response = client.get(reverse('user:profile:root'), {'token': token})
        tags = json.loads(response.content.decode('utf8'))['tags']
        self.assertEqual(tags, [])

    def test_location(self):
        # prepare data
        p1 = Province(name='P1')
        p1.save()
        c1 = City(province=p1, name='c1')
        c1.save()
        user = create_user('1', '1')
        token = user.token_info.token
        client = Client()

        # set province and city
        data = json.dumps({'location': [p1.id, c1.id]})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})

        # clear city
        data = json.dumps({'location': [p1.id, None]})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})
        response = client.get(reverse('user:profile:root'), {'token': token})
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['location'], [p1.id, None])

        # clear all
        data = json.dumps({'location': [None, None]})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})
        response = client.get(reverse('user:profile:root'), {'token': token})
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['location'], [None, None])

        # reset
        data = json.dumps({'location': [p1.id, c1.id]})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})

        # clear all
        data = json.dumps({'location': [None, None]})
        client.post(reverse('user:profile:root'), {'token': token, 'data': data})
        response = client.get(reverse('user:profile:root'), {'token': token})
        data = json.loads(response.content.decode('utf8'))
        self.assertEqual(data['location'], [None, None])

