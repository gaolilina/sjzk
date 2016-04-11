import json

from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from user.tests import create_user


class UserVisitorTestCase(TestCase):
    def test_visitor_total(self):
        # prepare users
        users, tokens = [], []
        for i in range(32):
            u = create_user(str(i))
            users.append(u)
            tokens.append(u.token_info.token)
        c = Client()
        user_ids = [i.id for i in users]

        # visitor total should be 0 at the moment
        token = tokens[0]
        r = c.get(reverse('user:visitor_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 0)
        r = c.get(reverse('user:visitor_today_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 0)

        # "visit" user 0
        for i in range(1, 32):
            c.get(reverse('user:profile_id', kwargs={'user_id': users[0].id}),
                  {'token': tokens[i]})
        r = c.get(reverse('user:visitor_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)
        r = c.get(reverse('user:visitor_today_total'), {'token': token})
        total = json.loads(r.content.decode('utf8'))['total']
        self.assertEqual(total, 31)

        # validate visitors
        r = c.get(reverse('user:visitor'), {'token': token})
        l = json.loads(r.content.decode('utf8'))
        for i in l:
            self.assertIn(i['id'], user_ids)
        r = c.get(reverse('user:visitor_today'), {'token': token})
        l = json.loads(r.content.decode('utf8'))
        for i in l:
            self.assertIn(i['id'], user_ids)
