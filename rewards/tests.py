from django.test import TestCase, Client
from django.urls import reverse
from .models import Ad, UserReward, AdViewToken
from django.contrib.auth.models import User
from unittest.mock import patch
from unittest import skip
from django.utils import timezone
from datetime import timedelta
import json
import pdb


# @skip("debug")
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

# @skip("debug")
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
        
# @skip("debug")
class RewardDeductionViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Add initial rewards to the user
        UserReward.objects.create(user=self.user, amount=100.0, transaction_type='earned')

        # Set up the client
        self.client = Client()

    def test_successful_reward_deduction(self):
        data = {'user_id': self.user.id, 'amount': 30.0}
        response = self.client.post(reverse('reward_deduction'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)

        # Check the new balance
        new_balance = sum(reward.amount for reward in UserReward.objects.filter(user=self.user))
        # pdb.set_trace()
        self.assertEqual(new_balance, 70.0)

    def test_deduction_exceeding_balance(self):
        data = {'user_id': self.user.id, 'amount': 150.0}
        response = self.client.post(reverse('reward_deduction'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_user(self):
        data = {'user_id': 9999, 'amount': 50.0}  # Non-existent user
        response = self.client.post(reverse('reward_deduction'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_invalid_data_format(self):
        data = {'user_id': self.user.id, 'amount': 'invalid'}  # Invalid amount format
        response = self.client.post(reverse('reward_deduction'), json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
class RewardBalanceViewTest(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Add rewards to the user
        UserReward.objects.create(user=self.user, amount=100.0, transaction_type='earned')
        UserReward.objects.create(user=self.user, amount=-50.0, transaction_type='deducted')

        # Set up the client
        self.client = Client()

    # @skip("debug")
    def test_get_reward_balance(self):
        response = self.client.get(reverse('reward_balance'), {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['reward_balance'], 50.0)

    # @skip("debug")
    def test_user_not_found(self):
        response = self.client.get(reverse('reward_balance'), {'user_id': 9999})
        self.assertEqual(response.status_code, 404)

    # @skip("debug")
    def test_no_user_id_provided(self):
        response = self.client.get(reverse('reward_balance'))
        self.assertEqual(response.status_code, 400)

class RewardHistoryViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.one_week_ago = timezone.now() - timedelta(weeks=1)
        UserReward.objects.create(user=self.user, amount=10.0, transaction_type='earned', created_at=self.one_week_ago)
        UserReward.objects.create(user=self.user, amount=-5.0, transaction_type='deducted', created_at=timezone.now())

        self.client = Client()

    # @skip("debug")
    def test_reward_history_success(self):
        response = self.client.get(reverse('reward_history'), {'user_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['reward_history']), 2)
        #check if the reward history values are correct
        self.assertEqual(response_data['reward_history'][0]['amount'], 10.0)
        self.assertEqual(response_data['reward_history'][1]['amount'], -5.0)
    
    # @skip("debug")
    def test_user_not_found(self):
        response = self.client.get(reverse('reward_history'), {'user_id': 9999})
        self.assertEqual(response.status_code, 404)

    # @skip("debug")
    def test_no_user_id_provided(self):
        response = self.client.get(reverse('reward_history'))
        self.assertEqual(response.status_code, 400)