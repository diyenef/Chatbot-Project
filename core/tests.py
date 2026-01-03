from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import UserProfile, ChatMessage


class TokenAndChatAPITest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('tester', password='pass')

    def test_profile_created(self):
        # UserProfile should exist and have default tokens
        profile = UserProfile.objects.get(user=self.user)
        self.assertIsNotNone(profile)
        self.assertGreaterEqual(profile.tokens, 0)

    def test_consume_token_and_chat(self):
        self.client.login(username='tester', password='pass')
        profile = self.user.userprofile
        start = profile.tokens

        # send a chat message
        resp = self.client.post('/api/chat/', data='{"message": "hello"}', content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('ok'))
        self.assertIn('reply', data)
        profile.refresh_from_db()
        self.assertEqual(profile.tokens, start - 1)

    def test_insufficient_tokens(self):
        self.client.login(username='tester', password='pass')
        profile = self.user.userprofile
        profile.tokens = 0
        profile.save()
        resp = self.client.post('/api/chat/', data='{"message":"hey"}', content_type='application/json')
        self.assertEqual(resp.status_code, 402)
        data = resp.json()
        self.assertFalse(data.get('ok'))
