from django.shortcuts import render
from django.http import JsonResponse
from .models import Ad
# Create your views here.

def get_ads(request):
    #Extract user data from the request
    user_id = request.GET.get('user_id')
    gender = request.GET.get('gender')
    country = request.GET.get('country')

    matching_ads = Ad.objects


    return JsonResponse({'ads': [user_id,gender,country]})  # Placeholder response