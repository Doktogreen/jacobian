from django.db import models
from users.models import Individual, Business
from typing_extensions import Literal
from typing import Callable


def validate_daily(value: str):
    if value < 50000.00 or value > 5000000.00:
        raise ValueError(f"value must be in the range 50000.00 to 5000000.00")
    return True

def validate_per_transaction(value: str) -> bool:
    if value < 10000.00 or value > 50000.00:
        raise ValueError(f"value must be in the range 10000.00 to 50000.00")
    return True

def validate_limit(limit_type: Literal["daily", "per_transaction"]) -> Callable:
    if limit_type == 'daily':
        return validate_daily
    return validate_per_transaction
# Create your models here.
class IndividualSettings(models.Model):
    user = models.OneToOneField(Individual, on_delete=models.CASCADE, related_name='settings', primary_key=True)
    daily_transfer_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=50000.00, validators=[validate_limit('daily')])
    daily_withdraw_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=50000.00, validators=[validate_limit('daily')])
    per_transaction_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=10000.00, validators=[validate_limit('per_transaction')])
    
    def __str__(self) -> str:
        return f"<IndividualSettings: {self.user.user.user.email}>"

class BusinessSettings(models.Model):
    user = models.OneToOneField(Business, on_delete=models.CASCADE, related_name='settings', primary_key=True)
    daily_transfer_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=50000.00, validators=[validate_limit('daily')])
    daily_withdraw_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=50000.00, validators=[validate_limit('daily')])
    per_transaction_limit = models.DecimalField(max_digits=11, decimal_places=2, null=False, blank=False, default=10000.00, validators=[validate_limit('per_transaction')])

    def __str__(self) -> str:
        return f"<BusinessSettings: {self.user.user.user.email}>"