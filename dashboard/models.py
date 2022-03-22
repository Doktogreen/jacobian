from django.db import models

# Create your models here.
class Register_Client(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.TextField()
    validated = models.BooleanField(default=True)
    bank_id = models.TextField()

class Balance(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey('Register_client', on_delete=models.CASCADE)
    available_balance = models.IntegerField(null=True)
    ledger_balance = models.IntegerField(null=True)
    currency = models.CharField(max_length=255, null=True)
    connected = models.BooleanField(null=True)
    created_at = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    last_updated = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    env = models.CharField( max_length=50, null=True)

class Income(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey('Register_client', on_delete=models.CASCADE)
    last_year_income = models.IntegerField(null=True)
    projected_yearly_income = models.IntegerField(null=True)
    transactions = models.IntegerField(null=True)

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey('Register_client', on_delete=models.CASCADE)
    trans_date = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    cleared_date = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    debit = models.IntegerField( null=True)
    credit = models.IntegerField( null=True)
    ref = models.CharField( max_length=50, null=True)
    bank = models.CharField( max_length=50, null=True)
    customer = models.CharField( max_length=50, null=True)
    account = models.CharField( max_length=50, null=True)
    created_at = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    last_updated = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)

class Identity(models.Model):
    id = models.AutoField(primary_key=True)
    customer_id = models.ForeignKey('Register_client', on_delete=models.CASCADE)
    fullname = models.CharField( max_length=50, null=True)
 
    bvn = models.CharField( max_length=50, null=True)
    score = models.CharField( max_length=50, null=True)
    env = models.CharField( max_length=50, null=True)
    created_at = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    last_updated = models.DateTimeField( auto_now=False, auto_now_add=False, null=True)
    dob = models.DateField( auto_now=False, auto_now_add=False, null=True)
    phone = models.CharField( max_length=50, null=True)
    email = models.CharField( max_length=50, null=True)
    address = models.CharField( max_length=50, null=True)
    status = models.CharField( max_length=50, null=True)
      