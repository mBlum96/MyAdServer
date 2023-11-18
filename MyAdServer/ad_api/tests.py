from django.test import TestCase, Client
from .models import Ad

class AdViewTests(TestCase):
    def setUp(self):
        # Create 5 ads targeted towards the same country and gender
        for i in range(1, 6):
            Ad.objects.create(
                name=f"Ad HK-F {i}",
                target_country="HK",
                target_gender="F",
                weight=i,
                image_url=f"https://example.com/ad_image_{i}.jpg",
                landing_url=f"https://example.com/ad_landing_{i}",
                reward=i
            )

        # Create 5 more ads with varying targets and weights
        countries = ["USA", "UK", "CN", "JP", "CA"]
        genders = ["M", "F", "M", "F", "M"]
        for i in range(6, 11):
            Ad.objects.create(
                name=f"Ad {countries[i-6]}-{genders[i-6]} {i}",
                target_country=countries[i-6],
                target_gender=genders[i-6],
                weight=i,
                image_url=f"https://example.com/ad_image_{i}.jpg",
                landing_url=f"https://example.com/ad_landing_{i}",
                reward=i
            )

    def test_weighted_ad_selection(self):
        client = Client()
        # Using a combination of image_url and landing_url as unique identifiers for ads
        ad_frequency = {f"{ad.image_url}|{ad.landing_url}": 0 for ad in Ad.objects.all()}

        # Make multiple requests to the endpoint
        for _ in range(100):
            response = client.get('/get-ads/', {'user_id': '1', 'gender': 'F', 'country': 'HK'})
            for ad in response.json().get('ads', []):
                ad_identifier = f"{ad['image url']}|{ad['landing_url']}"
                if ad_identifier in ad_frequency:
                    ad_frequency[ad_identifier] += 1
                else:
                    print("Identifier not found in ad_frequency:", ad_identifier)

        # Analyze the frequency of each ad
        print("Ad Frequencies:", ad_frequency)
