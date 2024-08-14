from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    height = models.FloatField()
    weight = models.FloatField()
    code = models.CharField(max_length=7, unique=True)  # Add this line

    def __str__(self):
        return f"{self.first_name} {self.last_name}"