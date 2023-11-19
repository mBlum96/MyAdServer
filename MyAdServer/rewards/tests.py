from django.test import TestCase, Client
from django.urls import reverse
from .models import Ad, UserReward, AdViewToken
from django.contrib.auth.models import User
from unittest.mock import patch
import json
from unittest import skip

class RewardUpdateViewTest(TestCase):

    def setUp(self):
        # Create a test user and admin user
        self.user = User.objects.create_user(username='user', password='testpass123')
        self.admin_user = User.objects.create_user(username='admin', password='adminpass123', is_staff=True)

        # Create a test ad
        self.ad = Ad.objects.create(name='Test Ad', reward=10)

        # Set up the client
        self.client = Client()

    # @skip("debug")
    def test_reward_update_success_by_admin(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('reward_update'), 
                                    json.dumps({'ad_id': self.ad.id, 'reward': 20}),
                                    content_type='application/json')
        self.ad.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ad.reward, 20)

    # @skip("debug")
    def test_reward_update_failure_by_non_admin(self):
        self.client.login(username='user', password='testpass123')
        response = self.client.post(reverse('reward_update'), 
                                    json.dumps({'ad_id': self.ad.id, 'reward': 30}),
                                    content_type='application/json')
        self.ad.refresh_from_db()
        self.assertNotEqual(self.ad.reward, 30)
        self.assertIn(response.status_code, [302, 403])  # Either redirect or forbidden
        #the above has two available because django will redirect to login
        #  page if not authenticated

    # @skip("debug")
    def test_invalid_json(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('reward_update'), 
                                    '{"ad_id": "test", "reward": "invalid"}',  # Invalid JSON
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request

    # @skip("debug")
    def test_missing_fields(self):
        self.client.login(username='admin', password='adminpass123')
        response = self.client.post(reverse('reward_update'), 
                                    json.dumps({'ad_id': self.ad.id}),  # Missing 'reward' field
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)  # Bad Request

class RewardAccumulationViewTest(TestCase):

    def setUp(self):
        # Create test users
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')

        # Create a test ad
        self.ad = Ad.objects.create(name="Test Ad", reward=10.0)

        # Create test tokens
        self.valid_token = AdViewToken.objects.create(user=self.user, ad=self.ad, token="validtoken", used=False)
        self.used_token = AdViewToken.objects.create(user=self.user, ad=self.ad, token="usedtoken", used=True)

        # Set up the client
        self.client = Client()

    # @skip("debug")
    def test_reward_accumulation_success(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('reward_accumulation'), 
                                    json.dumps({
                                        'user_id': self.user.id,
                                        'ad_id': self.ad.id,
                                        'token': self.valid_token.token,
                                        'reward': self.ad.reward
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(UserReward.objects.count(), 1)
        self.assertEqual(UserReward.objects.first().amount, self.ad.reward)

    # @skip("debug")
    def test_invalid_token(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('reward_accumulation'), 
                                    json.dumps({
                                        'user_id': self.user.id,
                                        'ad_id': self.ad.id,
                                        'token': 'invalidtoken',
                                        'reward': self.ad.reward
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # @skip("debug")
    def test_used_token(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('reward_accumulation'), 
                                    json.dumps({
                                        'user_id': self.user.id,
                                        'ad_id': self.ad.id,
                                        'token': self.used_token.token,
                                        'reward': self.ad.reward
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    # @skip("debug")
    def test_nonexistent_user_or_ad(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('reward_accumulation'), 
                                    json.dumps({
                                        'user_id': 9999,  # Non-existent user
                                        'ad_id': self.ad.id,
                                        'token': self.valid_token.token,
                                        'reward': self.ad.reward
                                    }),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)#we return invalid token
        #instead of 404 because we need a valid user id and a valid ad id 
        #to get a validation on the token since when they are faulty here,
        #we will never get 404 which is for faulty ad id or user id
        #so this is a redundant test but it is 23:25 right now 
        #so I am leaving it in
        

