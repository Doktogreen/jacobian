from rest_framework import serializers
from .models import Investment

class TransferSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    account_bank = serializers.CharField(max_length=150, required=True)
    account_number = serializers.CharField(max_length=10, required=True)
    amount = serializers.FloatField(required=True)
    beneficary_name = serializers.CharField(max_length=150, required=True)
    narration = serializers.CharField(max_length=150, required=False)


class AirtimeSerializer(serializers.Serializer):
    TYPE = [('airtime', 'airtime')]
    uuid = serializers.UUIDField(required=True)
    type = serializers.ChoiceField(choices=TYPE, required=True)
    service_provider = serializers.CharField(max_length=100)
    amount = serializers.IntegerField(required=True)
    phone = serializers.CharField(max_length=15)

class InvestmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = "__all__"
    # uuid = serializers.UUIDField(required=True)
    # amount = serializers.FloatField(required=True)
    # rate = serializers.FloatField(required=False)
    # days = serializers.IntegerField(required=False)
    # wht = serializers.FloatField(required=False)
    # total_amount = serializers.FloatField(required=False)
    # duration = serializers.IntegerField(required=True)
    # maturity_date = serializers.DateField(required=False)
    # start_date = serializers.DateField(required=False)
    # interest = serializers.FloatField(required=False)
    # status = serializers.CharField(max_length=15,required=False)

class CoporateCustomerSerializer(serializers.Serializer):
    savings_product = serializers.ChoiceField(choices=[
        (1, 'Simple Save'),
        (3, 'SME Savings'),
        (6, 'Simple Note'),
        (7, 'Wallet'),
    
    ])
    client_classification = serializers.ChoiceField(choices=[
        (25, 'Private Sector'),
        (26, 'Public Sector'),
        (27, "SME"),
        (70, "Investor"),
        (71, "Rewards")
    ])
    client_non_person_constituition = serializers.ChoiceField(choices=[
        (14, "LTD"),
        (15, "GTE"),
        (16, "Co-op"),
    ])
    client_non_person_main_business_line = serializers.ChoiceField(choices=[
        (57, 'Engineering'),
        (58, "IT"),
        (59, "Finance"),
        (63, "Trading"),
        (64, "Other"),
    ])