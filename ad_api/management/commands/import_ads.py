import json
import os
from django.core.management.base import BaseCommand
from ad_api.models import Ad


class Command(BaseCommand):
    help = 'Import ads from a JSON file'

    def handle(self, *args, **kwargs):
        # Get the path to the JSON file in the resources folder which is in the same directory as ad_api
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((__file__))))), 'resources', 'ad_campaigns.json')



        with open(file_path) as f:
            ads_data = json.load(f)

        for ad_data in ads_data:
            ad = Ad(
                name=ad_data['name'],
                image_url=ad_data['image_url'],
                landing_url=ad_data['landing_url'],
                weight=ad_data['weight'],
                target_country=ad_data['target_country'],
                target_gender=ad_data['target_gender'],
                reward=ad_data['reward']
            )
            ad.save()
        self.stdout.write(self.style.SUCCESS('Successfully imported ads'))
