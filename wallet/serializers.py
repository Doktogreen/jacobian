from rest_framework import serializers
from .models import Wallet, ReservedAccounts, WitMono, AccountTransaction


class FundInitiateSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    is_test = serializers.BooleanField()
    amount = serializers.IntegerField(required=True)
    card_number = serializers.CharField(max_length=255, min_length=3)
    expiry_year = serializers.CharField(max_length=255, min_length=2)
    expiry_month = serializers.CharField(max_length=255, min_length=2)
    cvv = serializers.CharField(max_length=3, min_length=3)
    suggested_auth = serializers.CharField(max_length=250)
    pin = serializers.IntegerField(required=True)
    charge_type = serializers.CharField(max_length=250)


class WalletSerializer(serializers.ModelSerializer):
    uuid = serializers.UUIDField(read_only=True)

    class Meta:
        model = Wallet
        fields = "__all__"


class WalletFundVerifySerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    reference = serializers.CharField(
        required=True, max_length=100, min_length=5)
    is_test = serializers.BooleanField(required=True)
    otp = serializers.IntegerField(required=True)


class ReservedAccountSerializer(serializers.ModelSerializer):
    is_test = serializers.BooleanField(read_only=True)
    uuid = serializers.CharField(read_only=True)

    class Meta:
        model = ReservedAccounts
        exclude = ['user', ]


class GetReservedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservedAccounts
        exclude = ('user',)


class GetMonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WitMono
        exclude = ('uuid',)


class WitMonoSerializer(serializers.ModelSerializer):
    class Meta:
        model = WitMono
        fields = "__all__"
        read_only = fields


class TransferToBankSerializer(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    amount = serializers.IntegerField()
    bank_code = serializers.CharField(max_length=10)
    pin = serializers.CharField(max_length=10, required=True)


class VerifyBankAccount(serializers.Serializer):
    account_number = serializers.CharField(max_length=10)
    bank_code = serializers.CharField(max_length=10)


class AccountTransactionSerializer(serializers.ModelSerializer):
    account = ReservedAccountSerializer()

    class Meta:
        model = AccountTransaction
        fields = "__all__"
        read_only = fields
