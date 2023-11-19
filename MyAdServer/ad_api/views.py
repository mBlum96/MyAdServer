from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.cache import cache
from .models import Ad
from .constants import MAX_ADS_SHOWN, NUMBER_OF_GROUPS,\
      GROUP_RANDOM, GROUP_MIX, GROUP_PCTR,GROUP_WEIGHT, ONE_HOUR
from django.middleware.csrf import get_token
from django.http import JsonResponse
import random
import logging
import requests

# Create your views here.

logger = logging.getLogger(__name__)

class AdSelectionView(View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = None
        self.gender = None
        self.country = None
        self.matching_ad_ids = []
        self.user_group = None

    def get(self, request, *args, **kwargs):
        self.initialize_request_attributes(request)
        ad_data = self.process_ad_request()
        if ad_data:
            return JsonResponse({'ads': ad_data})
        else:
            logger.debug(f"No ads available for the given criteria: User ID - {self.user_id}")
            return JsonResponse({'message': 'No ads available for the given criteria'}, status=404)

    def initialize_request_attributes(self, request):
        self.user_id = request.GET.get('user_id')
        self.gender = request.GET.get('gender')
        self.country = request.GET.get('country')
        self.user_group = int(self.user_id) % NUMBER_OF_GROUPS if self.user_id is not None else 0
        logger.debug(f"Request for ads received: User ID - {self.user_id}," 
                     f"Gender - {self.gender}, Country - {self.country}")

    def process_ad_request(self):
        matching_ads = self.get_matching_ads()
        if(matching_ads):
            self.set_ad_ids(matching_ads)
            selected_ads = self.select_ads(matching_ads)
            return self.format_ad_data(selected_ads)
        else:
            return None

    #this function is used to filter ads based on user data
    #I made it future proof by allowing for any number of attributes
    #to be used to filter ads
    def get_matching_ads(self):
            attributes ={
                'target_gender': self.gender,
                'target_country': self.country,
            }
            matching_ads = self.filter_ads_by_attributes(attributes)
            if not matching_ads and len(attributes)>1:
                matching_ads = self.try_fallback_ad_selection(attributes)
            return matching_ads
    
    def filter_ads_by_attributes(self, attributes):
            query = {}
            for key, value in attributes.items():
                if value:
                    query[key] = value
            return Ad.objects.filter(**query)
    
    def try_fallback_ad_selection(self,attributes):
        for key in list(attributes.keys()):
            temp_attributes = attributes.copy()
            temp_attributes.pop(key)
            matching_ads = self.filter_ads_by_attributes(temp_attributes)
            if matching_ads:
                return matching_ads
        return Ad.objects.none()
    
    def set_ad_ids(self, ads):
        self.matching_ad_ids = [ad.id for ad in ads]

    def select_ads(self,ads):
        if(self.user_group == GROUP_WEIGHT):
            return self.select_using_weighted_random(ads, MAX_ADS_SHOWN)
        elif(self.user_group == GROUP_PCTR):
            return self.select_using_pctr(ads, MAX_ADS_SHOWN)
        elif(self.user_group == GROUP_MIX):
            return self.select_using_mix(ads, MAX_ADS_SHOWN)
        else:
            return self.random_selection(ads, MAX_ADS_SHOWN)
        

    
    def format_ad_data(self, ads):
        return [{'image url': ad.image_url,\
                  'landing_url': ad.landing_url,\
                      'reward': ad.reward} for ad in ads]

    def select_using_weighted_random(self, ads, max_ads):
        selected = []
        ads = list(ads)
        random.shuffle(ads) # Shuffle to mitigate selection bias

        total_weight = sum(ad.weight for ad in ads)
        if total_weight == 0:
            return random.sample(ads, max_ads) # No weights, return random ads
        for _ in range(max_ads):
            r = random.uniform(0, total_weight)
            upto = 0
            for ad in ads:
                if upto + ad.weight >= r:
                    selected.append(ad)
                    break
                upto += ad.weight
        return selected

    def get_ctr_predictions(self):
        cache_key = f'ctr_predictions_{self.user_id}_{"_".join(map(str, self.matching_ad_ids))}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            logger.debug("Using cached CTR predictions")
            return cached_data
        
        ctr_request_url = f"https://predict-ctr-pmj4td4sjq-du.a.run.app/?user_id={self.user_id}&ad_campaign_ids={','.join(map(str, self.matching_ad_ids))}"
        logger.debug(f"CTR Prediction server request: {ctr_request_url}")
        response = requests.get(ctr_request_url)
        if response.status_code == 200:
            pctr_values = response.json().get('pctr', [])

            pctr_dict = dict(zip(self.matching_ad_ids, pctr_values))
            cache.set(cache_key, pctr_dict, ONE_HOUR)
            return pctr_dict
        else:
            logger.error(f"CTR Prediction server error: {response.status_code}")
            return {}
        
    def select_using_pctr(self, ads ,max_ads):
        selected = []
        ads = list(ads)
        pctr_dict = self.get_ctr_predictions()
        pctr_dict_sorted = sorted(pctr_dict.items(), key=lambda x: x[1], 
                                  reverse=True)
        logger.debug(f"CTR Prediction server response: {pctr_dict_sorted}")
        #select max_ads number of ads with highest pctr values
        for ad_id, _ in pctr_dict_sorted[:max_ads]:
            selected_ad = next((ad for ad in ads if ad.id == ad_id), None)
            if selected_ad:
                selected.append(selected_ad)
        logger.debug(f"Selected ads: {[ad.id for ad in selected]}")
        return selected
    
    def select_using_mix(self, ads, max_ads):
        selected = []
        ads = list(ads)
        pctr_choise = self.select_using_pctr(ads, max_ads)[0]
        selected.append(pctr_choise)
        ads.remove(pctr_choise)
        selected.extend(self.select_using_weighted_random(ads, max_ads-1))
        return selected
    
    def random_selection(self, ads, max_ads):
        return random.sample(list(ads), max_ads)

def get_csrf(request):
    # Force CSRF token to be generated
    token = get_token(request)
    # Send CSRF token in the cookie and as a separate header for convenience
    response = JsonResponse({'detail': 'CSRF cookie set'})
    response.set_cookie('csrftoken', token)
    response['X-CSRFToken'] = token
    return response