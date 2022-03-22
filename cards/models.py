from pyexpat import model
from django.db import models
from users.models import UserDetails

# Create your models here.


class Card(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    reference = models.CharField(max_length=10)
    
