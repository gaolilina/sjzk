import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from user.tests import create_user


class UserVisitorTestCase(TestCase):
    def test_visitor_total(self):
        # prepare users
        users, tokens = [], []
        for i in range(32):
            u = create_user(str(i), str(i))
            users.append(u)
            tokens.append(u.token_info.token)
        client = Client()
        user_ids = [i.id for i in users]

        # visitor total should be 0 at the moment
        token = tokens[0]
        r = client.get(reverse('user:visitor:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 0)
        r = client.get(reverse('user:visitor:today_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 0)

        # "visit" user 0
        for i in range(1, 32):
            client.get(
                reverse('user:profile:id', kwargs={'user_id': users[0].id}),
                {'token': tokens[i]})
        r = client.get(reverse('user:visitor:total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)
        r = client.get(reverse('user:visitor:today_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)

        # validate visitors
        r = client.get(reverse('user:visitor:root'), {'token': token})
        l = json.loads(r.content.decode('utf8'))
        for i in l:
            self.assertIn(i['id'], user_ids)
        r = client.get(reverse('user:visitor:today'), {'token': token})
        l = json.loads(r.content.decode('utf8'))
        for i in l:
            self.assertIn(i['id'], user_ids)
