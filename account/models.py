from users.models import UserDetails
from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal

Months = (

    ("January", "January"),
    ("February", "February"),
    ("March", "March"),
    ("April", "April"),
    ("May", "May"),
    ("June", "June"),
    ("July", "July"),
    ("August", "August"),
    ("September", "September"),
    ("October", "October"),
    ("November", "November"),
    ("December", "December")
)
CATEGORY = [
    ('ASSET', 'asset'),
    ('LIABILITY', 'liability'),
    ('INCOME', 'income'),
    ('EXPENSE', 'expense'),
    ('EQUITY', 'equity')
]
INV_STATUS = [
    ('Draft', 'Draft'),
    ('Sent', 'Sent'),
    ('Accepted', 'Accepted'),
    ('Declined', 'Declined'),
    ('Paid', 'Paid'),
    ('Overdue', 'Overdue')
]
ITEM = [
    ('Product', 'Product'),
    ('Service', 'Service')
]
# Create your models here.


class Customers(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    billing_address = models.CharField(max_length=100, blank=True, null=True)
    billing_city = models.CharField(max_length=100, blank=True, null=True)
    billing_country = models.CharField(max_length=100, blank=True, null=True)
    shipping_address = models.CharField(max_length=100, blank=True, null=True)
    shipping_city = models.CharField(max_length=100, blank=True, null=True)
    shipping_country = models.CharField(max_length=100, blank=True, null=True)


class Vendor(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    account_number = models.CharField(max_length=20, blank=True, null=True)
    account_name = models.CharField(max_length=200, blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)


class Product(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    type = models.CharField(choices=ITEM, max_length=100, default="Product")

# class Service(models.Model):
#     user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100, blank=True, null=True)
#     timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
#     description = models.CharField(max_length=100, blank=True, null=True)
#     price = models.FloatField(blank=True, null=True)


class Asset(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)


class Liability(models.Model):
    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)


class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    type = models.CharField(choices=CATEGORY, max_length=100)
    currency = models.CharField(max_length=100, default='NGN')
    description = models.TextField()
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

    def calculate_asset_balance(self, credit, debit):
        if (credit != 0):
            amount = Decimal(credit)* -1
        elif(debit != 0):
            amount = Decimal(debit) 
        self.balance += amount
        self.save()

    def calculate_liability_balance(self, credit, debit):
        if (credit != 0):
            amount = Decimal(credit)
        elif(debit != 0):
            amount = Decimal(debit) * -1
        self.balance += amount
        self.save()

    def calculate_income_balance(self, credit, debit):
        if (credit != 0):
            amount = Decimal(credit)
        elif(debit != 0):
            amount = Decimal(debit) * -1
        self.balance += amount
        self.save()

    def calculate_expense_balance(self, credit, debit):
        if (credit != 0):
            amount = Decimal(credit)* -1
        elif(debit != 0):
            amount = Decimal(debit) 
        self.balance += amount
        self.save()

    def calculate_equity_balance(self, credit, debit):
        if (credit != 0):
            amount = Decimal(credit)
        elif(debit != 0):
            amount = Decimal(debit) * -1
        self.balance += amount
        self.save()


class Invoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customers, on_delete=models.CASCADE)
    id = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False)
    invoice_number = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    accepted = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    status = models.CharField(
        choices=INV_STATUS, max_length=100, default="Draft")
    tax = models.FloatField()


class InvoiceItem(models.Model):
    inv_uuid = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def getamount(self):
        return self.product.price

    def gettotal(self):
        return self.product.price * self.quantity


class Journal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    reference = models.UUIDField(default=uuid.uuid4, editable=False)
    total_credit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    total_debit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)


class JournalEntry(models.Model):
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    credit = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
