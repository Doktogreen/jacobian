from django.db import models
from users.models import UserDetails

# Create your models here.
STATUS = (
    ("Pending", "Pending"),
    ("Approved", "Approved"),
    ("Denied", "Denied"),
    ("Completed", "Completed"),
)
CONTRACT = (
    ("Sent", "Sent"),
    ("Withdrawn", "Withdrawn"),
    ("Denied", "Denied"),
    ("Approved", "Approved")
)
CURRENCY = (
    ("NGN", "NGN"),
)

class Investment(models.Model):
    uuid = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    amount = models.FloatField(default=0.0, blank=True, null=True)
    rate = models.FloatField(default=0.0, blank=True, null=True)
    days = models.IntegerField( blank=True, null=True)
    wht = models.FloatField(default=10.0, blank=True, null=True)
    total_amount = models.FloatField(default=0.0, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    maturity_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    interest = models.FloatField(default=10.0, blank=True, null=True)
    status = models.CharField(
        max_length=90, choices=STATUS, blank=True, null=True)
    currency = models.CharField(
        max_length=90, choices=CURRENCY, default="NGN", blank=True, null=True)
    contract_status = models.CharField(
        max_length=90, choices=CONTRACT, blank=True, null=True)