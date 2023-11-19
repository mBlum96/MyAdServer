from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from .models import Ad, UserReward
import json
import logging

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

class RewardAccumulationView(View)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.reward = None
        self.ad_id = None
    
    def post(self, request, *args, **kwargs):
