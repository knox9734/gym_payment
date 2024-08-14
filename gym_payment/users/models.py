from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    height = models.FloatField()
    weight = models.FloatField()
    code = models.CharField(max_length=7, unique=True)  # Add this line

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField()

    def save(self, *args, **kwargs):
        if not self.expiration_date:
            self.expiration_date = timezone.now().date() + timedelta(days=25)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.payment_date} to {self.expiration_date}"