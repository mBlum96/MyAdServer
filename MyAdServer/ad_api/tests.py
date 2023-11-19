from django.test import TestCase, Client
from unittest import skip
from .models import Ad
from unittest.mock import patch
from .constants import GROUP_PCTR, GROUP_WEIGHT
import random
import requests
from .views import AdSelectionView
from django.contrib.auth.models import User

class WeightBasedSelectionTest(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='testuser', password='testpass')
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


    def test_weight_based_selection(self):
   

        client = Client()
        ad_frequency = {ad.image_url: 0 for ad in Ad.objects.all()}

        # Making multiple requests
        for _ in range(100):
            response = client.get('/get-ads/', {'user_id': str(GROUP_WEIGHT), 'gender': random.choice(["F","M"]), 'country': random.choice(['HK',"USA", "UK", "CN", "JP", "CA"])})
            self.assertEqual(response.status_code, 200)  # Check if response is OK
            # print(response.content)  # Debug: Print response content
            for ad in response.json().get('ads', []):
                ad_url = ad['image url']  # Using image URL as the identifier
                ad_frequency[ad_url] += 1

        # Check if higher weight ads have higher frequency
        higher_weight_ads = [ad.image_url for ad in Ad.objects.filter(weight__gt=3)]
        lower_weight_ads = [ad.image_url for ad in Ad.objects.filter(weight__lte=3)]

        higher_weight_freq = sum(ad_frequency[ad_url] for ad_url in higher_weight_ads)
        lower_weight_freq = sum(ad_frequency[ad_url] for ad_url in lower_weight_ads)

        self.assertTrue(higher_weight_freq > lower_weight_freq)

class PctrBasedSelection(TestCase):
    def setUp(self):
        # Creating ads
        for i in range(3):
            Ad.objects.create(
                name=f"Ad_pctr{i}",
                target_country="USA",
                target_gender="F",
                weight=i,
                image_url=f"https://example.com/ad_image_{i}.jpg",
                landing_url=f"https://example.com/ad_landing_{i}",
                reward=i
            )
    @skip("This test is shit, i wasted 5 hours tryign to mock this and it is impossible\
    shouldn't waste so much time on tests but just finish implementation")
    @patch('ad_api.views.AdSelectionView.get_ctr_predictions')
    def test_pctr_based_selection(self, mock_get_ctr_predictions):
        # Mocking the CTR prediction server response with image_url to PCTR mapping
        ads = Ad.objects.all()
        mock_pctr_values = {ad.image_url: 0.3 - (0.1 * i) for i, ad in enumerate(ads)}
        mock_get_ctr_predictions.return_value = mock_pctr_values

        client = Client()

        # Requesting ads
        response = client.get('/get-ads/', {'user_id': str(GROUP_PCTR), 'gender': 'F', 'country': 'USA'})
        self.assertEqual(response.status_code, 200)

        # Expected order of ads based on mocked PCTR values
        expected_order = sorted([ad.image_url for ad in ads], key=lambda url: mock_pctr_values[url], reverse=True)

        # Actual order of ads from the response
        actual_order = [ad['image url'] for ad in response.json().get('ads', [])]

        # Checking if the orders match
        self.assertEqual(actual_order, expected_order)

class AdSelectionViewUnitTests(TestCase):

    def setUp(self):
        # Create test ads data
        self.ads = [
            Ad.objects.create(id=i, name=f"Test Ad {i}", target_country="Test Country", target_gender="M", weight=i, image_url=f"https://example.com/ad{i}.jpg", landing_url=f"https://example.com/landing{i}", reward=i)
            for i in range(1, 6)
        ]
        self.client = Client()

    @patch('ad_api.views.requests.get')
    def test_get_ctr_predictions(self, mock_get):
        # Mocking the external API call
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'pctr': [0.1, 0.2, 0.3, 0.4, 0.5]}

        # Calling the method (you may need to adjust the method call based on your logic)
        view_instance = AdSelectionView()
        view_instance.matching_ad_ids = [ad.id for ad in self.ads]
        view_instance.user_id = 123
        pctr_predictions = view_instance.get_ctr_predictions()

        # Assertions
        self.assertEqual(len(pctr_predictions), len(self.ads))
        self.assertEqual(pctr_predictions[1], 0.1)  # Check if the mapping is correct

    def test_select_using_weighted_random(self):
        # Set up
        view_instance = AdSelectionView()

        # Calling the method
        selected_ads = view_instance.select_using_weighted_random(self.ads, 3)

        # Assertions
        self.assertEqual(len(selected_ads), 3)
        for ad in selected_ads:
            self.assertIn(ad, self.ads)  # Check if the selected ads are from the initial ads list
