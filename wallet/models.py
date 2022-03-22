from __future__ import unicode_literals
import decimal
from django.contrib.auth.models import User
import uuid
from django.db import models
from middleware.response import error_response
from sendgrid.helpers import mail
from users.models import UserDetails
from transaction.models import Ledger, Transaction
from django.utils import timezone
from account.views import send_email
from decimal import Decimal
from django.core.exceptions import ValidationError
# Create your models here.
STATUS = (
    ("ACTIVE", "ACTIVE"),
    ("INACTIVE", "INACTIVE")
)


class Wallet(models.Model):
    id = models.AutoField(primary_key=True, default=None)
    wallet_id = models.UUIDField(default=uuid.uuid4, editable=True)
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    pocketReferenceId = models.CharField(
        max_length=200, default=None, null=True)
    pocketAccountNumber = models.CharField(
        max_length=200, default=None, blank=True, null=True)
    customerExternalRef = models.CharField(
        max_length=200, default=None, null=True)
    balance = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    lastBalance = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    status = models.CharField(max_length=90, choices=STATUS, null=True)
    createdAt = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(default=timezone.now)

    def deposit(self, value: float, transaction_type: str, status: str, payment_reference=None, payment_response=None):
        """Deposits a value to the wallet.
        Also creates a new transaction with the deposit
        value.
        """
        value = Decimal(value)

        transaction = Transaction.objects.create(
            user=self.user, transaction_type=transaction_type, status=status, amount=value, type='credit',
            payment_reference=payment_reference, payment_response=payment_response)
        transaction.save()

        Ledger.objects.create(user=self.user, transaction_type='credit', opening_balance=self.balance,
                              amount=value, ledger_entity=self.id, comment='CREDIT FOR WALLET')
        mail_subject = "simplefi wallet credit"
        mail_html_contect = "<p>Hello " + self.user.user.first_name + "," + "</p><p> You have a transaction notification on your Simplefi wallet.</p><p>reference: "+transaction.reference+"</p><p>amount: "+str(
            value)+"</p><p>type: 'credit'</p><p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
        send_email(self.user.user.email, mail_subject, mail_html_contect)
        self.lastBalance = self.balance
        self.balance += value
        self.save()

    def withdraw(self, value: float, transaction_type: str, status: str, payment_reference=None, payment_response=None):

        value = Decimal(value)

        if self.get_balance() < value:
            return error_response(status=200, message="Insufficent fund")

        if self.check_limit(value, 'withdraw'):
            raise ValueError('Withdrawal Limit Exceeded')
        transaction = Transaction.objects.create(
            user=self.user, transaction_type=transaction_type, status=status, amount=value, type='debit',
            payment_reference=payment_reference, payment_response=payment_response)
        transaction.save()

        Ledger.objects.create(user=self.user, transaction_type='debit', opening_balance=self.balance,
                              amount=-value, ledger_entity=self.id, comment='DEBIT FOR WALLET')
        mail_subject = "simplefi wallet debit"
        mail_html_contect = "<p>Hello " + self.user.user.first_name + "," + "</p><p> You have a transaction notification on your Simplefi wallet.</p><p>reference: "+transaction.reference+"</p><p>amount: "+str(
            value)+"</p><p>type: 'debit'</p><p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
        send_email(self.user.user.email, mail_subject, mail_html_contect)
        self.lastBalance = self.balance
        self.balance -= value
        self.save()

    def pending(self, value: float, transaction_type: str, payment_reference=None, payment_response=None, status='SPV'):
        if self.check_limit(value, 'withdraw'):
            raise ValueError('Withdrawal Limit Exceeded')
        Transaction.objects.create(
            user=self.user, transaction_type=transaction_type, status=status, amount=value, type='debit',
            payment_reference=payment_reference, payment_response=payment_response)
        self.save()

    def get_balance(self):

        try:
            ledger = Ledger.objects.filter(
                user=self.user).latest('credit_date')
        except Ledger.DoesNotExist:
            return self.balance
        return ledger.opening_balance + ledger.amount

    def transfer(self, wallet, value):
        """Transfers an value to another wallet.
        Uses `deposit` and `withdraw` internally.
        """
        if self.get_balance() < value:
            return error_response(status=200, message="Insufficent fund")

        if self.check_limit(Decimal(value), 'transfer'):
            raise ValueError('Transfer Limit Exceeded')
        self.withdraw(value)
        wallet.deposit(value)

    def check_limit(self, value, action):
        if hasattr(self.user, 'individual'):
            actions = {
                'transfer': self.user.individual.settings.daily_transfer_limit,
                'withdraw': self.user.individual.settings.daily_withdraw_limit
            }
        else:
            actions = {
                'transfer': self.user.business.settings.daily_transfer_limit,
                'withdraw': self.user.business.settings.daily_withdraw_limit
            }
        transacted = Ledger.get_daily_transaction_sum(self.user)
        limit = actions[action]

        return transacted + value > limit

    def __str__(self):
        return self.user.user.username

    def __unicode__(self):
        return str(self.id)

    def transfer(self):
        pass
    # @admin.display(boolean=True)

    def user_email(self):
        return self.user.user.email


class ReservedAccounts(models.Model):
    user = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    accountName = models.CharField(max_length=90, default=None)
    accountNumber = models.CharField(max_length=90, default=None)
    bankCode = models.CharField(max_length=40, default=None)
    bankName = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.accountName

# Saves withmono  details


class WitMono(models.Model):
    uuid = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True, blank=True)
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=90, default=None)  # withZZZ
    name = models.CharField(max_length=150, null=True)
    bvn = models.CharField(max_length=90, null=True)
    acct_number = models.FloatField(null=True)
    balance = models.FloatField(null=True)
    income = models.FloatField(null=True)
    credit_score = models.FloatField(null=True)


class AccountTransaction(models.Model):
    account = models.ForeignKey(ReservedAccounts, on_delete=models.CASCADE)
    type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    createdOn = models.CharField(max_length=200)
    completedOn = models.CharField(max_length=200)
    description = models.CharField(max_length=200, null=True)
    completed = models.BooleanField(default=True)
    paymentMethod = models.CharField(max_length=50)
    providerCode = models.CharField(max_length=50, null=True)
    transactionReference = models.CharField(max_length=50)
    paymentReference = models.CharField(max_length=50)
    merchantCode = models.CharField(max_length=50)
    merchantName = models.CharField(max_length=100)
    settleInstantly = models.BooleanField(null=True)
    payableAmount = models.FloatField(default=0.0)

    def __str__(self):
        return self.transactionReference


class Remita(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
