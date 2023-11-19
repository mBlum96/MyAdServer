from django.db import models
from django.db import models
from django.contrib.auth.models import User
from ad_api.models import Ad

class UserReward(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    ad = models.ForeignKey(Ad, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=50)  # e.g., 'earned', 'used'

    def __str__(self):
        return f"{self.user.username} - {self.amount}"
