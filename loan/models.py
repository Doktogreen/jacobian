from django.db import models
from django.contrib.auth.models import User
from users.models import UserDetails
from services.models import Investment

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


class Prediction(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return self.user.name

class CRMLoan(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=11,decimal_places=2)
    clientId = models.CharField(max_length=12, blank=True,)
    loanId = models.CharField(max_length=12, blank=True,)
    payment_duration = models.IntegerField(null=True)
    contract_status = models.CharField(
        max_length=90, choices=STATUS, blank=True, null=True)
    
class Loan(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=50, decimal_places=2)
    total_repayment = models.DecimalField(
        max_digits=50, decimal_places=2, blank=True,)
    crm_loan_id = models.IntegerField(blank=True, null=True)
    repayment_amount = models.DecimalField(
        max_digits=50, decimal_places=2, blank=True,)
    purpose = models.TextField()
    amount_paid=models.DecimalField(
        max_digits=50, decimal_places=2, blank=True, default=0.00)
    payment_duration = models.IntegerField(null=True)
    request_date = models.DateTimeField(auto_now=False, auto_now_add=True)
    interest = models.DecimalField(
        max_digits=50, decimal_places=2, blank=True,)
    admin_fee = models.DecimalField(
        max_digits=50, decimal_places=2, default=2500.00, blank=True,)
    penalties = models.CharField(max_length=120, blank=True,)
    status = models.CharField(
        max_length=90, choices=STATUS, blank=True, null=True)
    currency = models.CharField(
        max_length=90, choices=CURRENCY, default="NGN", blank=True, null=True)
    maturity_date = models.DateTimeField(blank=True, null=True)
    contract_status = models.CharField(
        max_length=90, choices=STATUS, blank=True, null=True)

    def __str__(self):
        return str(self.user)


class Repayment(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=50, decimal_places=2)
    paid = models.BooleanField(default=False)
    amount_due = models.DecimalField(max_digits=50, decimal_places=2)
    # interest_due = models.DecimalField(max_digits=50, decimal_places=3, )
    amount_paid = models.DecimalField(max_digits=50, decimal_places=2)
    outstanding = models.DecimalField(max_digits=50, decimal_places=2)
    payment_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(
        auto_now=False, auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return str(self.loan)

    def __unicode__(self):
        return self.user.email


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(
        choices=CONTRACT, max_length=10, null=True, blank=True)
    contract_id = models.CharField(max_length=100, null=True, blank=True)
    template_name = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=100, null=True, blank=True)
    signers_id = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    contract_pdf_url = models.CharField(max_length=250, null=True, blank=True)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    loan = models.OneToOneField(
        Loan, on_delete=models.CASCADE, blank=True, null=True)
    investment = models.OneToOneField(
        Investment, on_delete=models.CASCADE, blank=True, null=True)


# class Payments(models.Model):
# 	title = models.CharField(max_length=120)
# 	amount = models.TextField()
# 	updated = models.DateTimeField(auto_now = True, auto_now_add = False)
# 	timestamp = models.DateTimeField(auto_now = False, auto_now_add = True)

# 	def __unicode__(self):
# 		return self.title
