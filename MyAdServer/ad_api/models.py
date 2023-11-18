from django.db import models

class Ad(models.Model):
    id = models.AutoField(primary_key=True)  # Unique identifier for each ad
    name = models.CharField(max_length=255, null=True, blank=True)  # Name of the ad
    image_url = models.URLField(null=True, blank=True) # URL of the ad's image
    landing_url = models.URLField(null=True, blank=True)  # URL where the user is redirected after clicking the ad
    weight = models.IntegerField(null=True, blank=True) # Weight for ad sorting
    target_country = models.CharField(max_length=100,null=True, blank=True)  # Target country for the ad
    target_gender = models.CharField(max_length=1, null=True, blank=True)  # Target gender ('M' or 'F')
    reward = models.FloatField(null=True, blank=True)  # Reward for interacting with the ad

    def __str__(self):
        return self.name
