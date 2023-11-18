from django.shortcuts import render
from django.http import JsonResponse
from .models import Ad
from .constants import MAX_ADS_SHOWN
import random
# Create your views here.

def weighted_random_selection(ads, max_ads):
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

#this function is used to filter ads based on user data
#I made it future proof by allowing for any number of attributes
#to be used to filter ads
def get_matching_ads(attributes):
        query = {}
        for key, value in attributes.items():
            if value:
                query[key] = value
        return Ad.objects.filter(**query)

def get_ads(request): 
    #Extract user data from the request
    user_id = request.GET.get('user_id')
    gender = request.GET.get('gender')
    country = request.GET.get('country')
    attributes ={
        'target_gender': gender,
        'target_country': country,
    }

    matching_ads = get_matching_ads(attributes)
    if not matching_ads and len(attributes) > 1:
        original_key_list = list(attributes.keys())
        for key in original_key_list:
            temp_attributes = attributes.copy()#creating a copy 
            #of the attributes dictionary to avoid modifying the original
            temp_attributes.pop(key)
            matching_ads = get_matching_ads(temp_attributes)
            if matching_ads:
                break

    if matching_ads:
        selected_ads= weighted_random_selection(matching_ads, MAX_ADS_SHOWN)

        ad_data = [{'image url': ad.image_url,'landing_url': ad.landing_url,
                    'reward': ad.reward}
                    for ad in selected_ads ]
        return JsonResponse({'ads': ad_data})

    return JsonResponse({
        'message': 'No ads available for the given criteria'}, status=404)

    