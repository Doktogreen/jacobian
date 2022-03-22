from rest_framework import serializers
from .models import Loan, Repayment, Contract, CRMLoan


class CreateLoanSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    amount = serializers.IntegerField(required=True)
    purpose = serializers.CharField(required=True)
    payment_duration = serializers.IntegerField(required=True)


class LoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ('amount', 'purpose', 'payment_duration')


class CreateLoanSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ('user', 'amount', 'purpose',
                  'payment_duration', 'status', 'maturity_date')


class ApplyLoanSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=True)
    amount = serializers.IntegerField(required=True)
    purpose = serializers.CharField(required=True)
    payment_duration = serializers.IntegerField(required=True)


class RepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repayment
        fields = "__all__"


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = "__all__"


class CRMLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = CRMLoan
        fields = "__all__"


class LoanKYCSerializer(serializers.Serializer):
    GENDER = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Others', 'Others'),
    ]
    idType = [
        ('nin', 'nin'),
        ('inec', 'inec'),
        ('ibvn', 'ibvn'),
        ('frsc', 'frsc'),
        ('passport', 'passport')
    ]
    ACCOUNT_TYPE = [
        ('savings', 'savings'),
        ('current', 'current')
    ]

    accountNo = serializers.CharField(max_length=10)
    accType = serializers.ChoiceField(ACCOUNT_TYPE, )
    Bank = serializers.CharField(max_length=150, )
    nextofkin_name = serializers.CharField(max_length=150, )
    nok_phone = serializers.CharField(min_length=11)
    nextofkin_title = serializers.CharField(max_length=150, )
    nextofkin_email = serializers.EmailField()
    NetMonthlyIncome = serializers.CharField(max_length=120, )
    employeraddress = serializers.CharField(max_length=120, )
    companyName = serializers.CharField(max_length=150, )
    companyemail = serializers.EmailField()
    employeeStartDate = serializers.DateField()
    obligation = serializers.BooleanField()
    staff_id = serializers.CharField(max_length=150, )
