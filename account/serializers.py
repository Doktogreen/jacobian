from rest_framework import serializers

from .models import Invoice, Journal, JournalEntry, Customers, Product, Vendor, Asset, Liability, Account


# class ServiceSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Service
#         fields = "__all__"


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = "__all__"


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = "__all__"


class LiabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Liability
        fields = "__all__"


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'type', 'description',
                  'category', 'balance', ]


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = "__all__"


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = "__all__"


class TemplateInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['status', 'accepted', 'paid', ]
