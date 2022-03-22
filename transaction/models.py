from django.db import models
from django.db.models import Sum
from transaction.utils import generate_transaction_reference
from users.models import UserDetails
from datetime import datetime
# Create your models here.

class Transaction(models.Model):

    TRANSACTION_TYPE = [
        ('Bank-Transfer', 'Bank-Transfer'),
        ('Top-Up', 'Top-Up'),
        ('Airtime', 'Airtime'),
        ('Data', 'Data'),
        ('Bill', 'Bill'),
        ('Tuition', 'Tuition'),
        ('loan', 'loan'),
        ('loan-repayment', 'Loan Repayment')
    ]
    STATUS = [
        ('NEW', 'Initiated Trasaction'),
        ('SPV', 'PENDING VALIDATION'),
        ('FAILED', 'FAILED'),
        ('SUCCESS', 'SUCCESS')
    ]

    TYPE = [
        ('debit', 'debit'),
        ('credit', 'credit'),
    ]
    transaction_type = models.CharField(
        choices=TRANSACTION_TYPE, max_length=50)
    user = models. ForeignKey(UserDetails, on_delete=models.CASCADE)
    status = models.CharField(
        choices=STATUS, max_length=200, default=STATUS)
    type = models.CharField(
        choices=TYPE, max_length=100, null=True)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    balance = models.DecimalField(max_digits=11, decimal_places=2, null=True, blank=True)
    reference = models.CharField(max_length=150, blank=True, null=True, unique=True)
    narration = models.TextField(max_length=200, null=True, blank= True)
    payment_reference = models.CharField(max_length=200)
    payment_response = models.CharField(max_length=200)
    currency = models.CharField(max_length=5, default='NGN')
    created_date = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status

    def save(self, *args, **kwargs):
        if self.status and not self.__status:
            self.created_date = datetime.now()
        if self.reference is None:
            self.reference = generate_transaction_reference()
        if self.balance is None:
            ud = UserDetails.objects.get(id=self.user.id)
            self.balance = ud.wallet.get_balance()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.reference


class Ledger(models.Model):
    opening_balance = models.DecimalField(max_digits=11, decimal_places=2)
    amount = models.DecimalField(
        max_digits=11, decimal_places=2, editable=False)
    comment = models.CharField(
        max_length=250, blank=True, null=True, editable=False)
    credit_date = models.DateTimeField(auto_now_add=True, editable=False)
    is_test = models.BooleanField(default=1, editable=False)
    transaction_type = models.CharField(
        max_length=250, blank=True, editable=False)
    ledger_entity = models.CharField(max_length=20, editable=False)
    user = models.ForeignKey(
        UserDetails, on_delete=models.CASCADE, editable=False)

    def __str__(self):
        return self.ledger_entity

    @staticmethod
    def get_daily_transaction_sum(user):
        today = datetime.today().date()
        amount = Ledger.objects.filter(user=user, transaction_type='debit', credit_date__date=today).aggregate(Sum('amount'))
        if amount.get('amount__sum', 0) is None:
            return 0
        return amount.get('amount__sum', 0)
