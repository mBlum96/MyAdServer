from django.db import models
from ad_api.models import Ad
from django.contrib.auth.models import User

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    ad = models.ForeignKey(Ad, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=50)  # e.g., 'earned', 'used'

    def __str__(self):
        return f"{self.user.username} - {self.amount}"

class AdViewToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.token
