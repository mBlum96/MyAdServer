from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from rewards.models import Ad, UserReward, AdViewToken
import json
import logging
import pdb

class RewardUpdateView(View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ad_id = None
        self.reward = None

    @method_decorator(user_passes_test(lambda u: u.is_staff))  # Restrict to admin users
    def post(self, request, *args, **kwargs):
        try:
            self.initialize_request_attributes(request)
            self.update_reward()
            return JsonResponse({'message': 'Reward updated successfully'})
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except KeyError:
            return JsonResponse({'message': 'Required fields missing'}, status=400)
        except Ad.DoesNotExist:
            return JsonResponse({'message': 'Ad not found'}, status=404)
        except ValueError:
            return JsonResponse({'message': 'Invalid value for reward'}, status=400)
        except Exception as e:
            # Log the exception for debugging
            return JsonResponse({'message': str(e)}, status=500)

    def initialize_request_attributes(self, request):
        data = json.loads(request.body)
        self.ad_id = data['ad_id']
        self.reward = float(data['reward'])  # Assuming reward is a numeric value

    def update_reward(self):
        try:
            ad = Ad.objects.get(id=self.ad_id)
            ad.reward = self.reward
            ad.save()
            # logger.debug(f"Reward updated for Ad ID - {self.ad_id}")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return HttpResponseServerError('Internal Server Error')

#accumulation is called when a user clicks on an ad
class RewardAccumulationView(View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.reward = None
        self.ad_id = None
        self.token = None
    
    def post(self, request, *args, **kwargs):
        try:
            
            # pdb.set_trace()
            self.initialize_request_attributes(request)
            if not self.is_valid_token():
                return JsonResponse({'message': 'Invalid token'}, status=400)
            return self.accumulate_reward()

        except Exception as e:
            # handle exceptions
            return JsonResponse({'message': str(e)}, status=500)
    
    def initialize_request_attributes(self, request):
        # pdb.set_trace()
        data = json.loads(request.body)
        self.user_id = data['user_id']
        self.ad_id = data['ad_id']
        self.reward = float(data['reward'])
        self.token = data['token']
        

    def is_valid_token(self):
        try:
            ad_view_token = AdViewToken.objects.get(user_id=self.user_id, ad_id=self.ad_id, token=self.token, used=False)
            ad_view_token.used = True
            ad_view_token.save()
            return True
        except AdViewToken.DoesNotExist:
            return False
        except Exception as e:
            logger.error(f"Error in is_valid_token: {e}")
            return False

    
    def accumulate_reward(self):
        try:
            # pdb.set_trace()
            user = User.objects.get(id=self.user_id)
            ad = Ad.objects.get(id=self.ad_id)
            amount = 0
            user_reward, created = UserReward.objects.get_or_create(user=user, ad=ad, amount=amount, transaction_type='earned')
            if created:
                user_reward.amount = ad.reward 
                user_reward.transaction_type = 'earned'
                user_reward.save()
                return JsonResponse({'message': 'Reward accumulated successfully'})
            else:
                return JsonResponse({'message': 'Reward already given for this ad'}, status=400)
        except (User.DoesNotExist, Ad.DoesNotExist) as e:
            logger.error(f"Error in accumulate_reward: {e}")
            return JsonResponse({'message': str(e)}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error in accumulate_reward: {e}")
            return JsonResponse({'message': 'Internal Server Error'}, status=500)
