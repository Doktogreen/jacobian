from django.conf import settings
from rest_framework import serializers
from .models import UserDetails, Individual, Business, Employee, NextOfKin, IndividualDocuments, BusinessDocument, Guarantor
from django.contrib.auth.models import User
from rest_framework.mixins import CreateModelMixin
from loan.models import Loan
from settings.models import IndividualSettings, BusinessSettings
from settings.serializers import IndividualSettingsSerializer, BusinessSettingsSerializer
import requests

idType = [
    ('nin', 'nin'),
    ('inec', 'inec'),
    ('none', 'none')
]

AccountType = [
    ("Individual", "Individual"),
    ("Business", "Business")
]


class UserVerifyKYCSerializer(serializers.ModelSerializer):

    nextofkin_name = serializers.CharField(max_length=100)
    nextofkin_title = serializers.CharField(max_length=100)
    nextofkin_email = serializers.CharField(max_length=100)

    class Meta:
        model = Individual
        fields = (
            'identification_type', 'identification_number',
            'address', 'gender', 'date_of_birth',
            'state', 'lga', 'nextofkin_name',
            'nextofkin_title', 'nextofkin_email'
        )


class NextofKinSerializer(serializers.ModelSerializer):
    class Meta:
        model = NextOfKin
        fields = "__all__"


class VerifyKYCSerializer(serializers.Serializer):
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
    identification_type = serializers.ChoiceField(choices=idType)
    identification_number = serializers.CharField(max_length=11)
    gender = serializers.ChoiceField(GENDER, required=False)
    date_of_birth = serializers.DateField(required=False)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=11, min_length=11, required=False)
    firstname = serializers.CharField(max_length=150, required=False)
    lastname = serializers.CharField(max_length=150, required=False)
    address = serializers.CharField(max_length=150, required=False)
    origin = serializers.CharField(max_length=150, required=False)
    state = serializers.CharField(max_length=150, required=False)
    lga = serializers.CharField(max_length=150, required=False)
    image = serializers.CharField(style={'base_template': 'textarea.html'})


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=150, required=True)
    firstname = serializers.CharField(max_length=150, required=False)
    lastname = serializers.CharField(max_length=150, required=False)
    business_name = serializers.CharField(max_length=200, required=False)
    account_type = serializers.ChoiceField(AccountType, required=True)
    bvn = serializers.CharField(max_length=20, required=False)

    def validate_email(self, value):
        if User.objects.filter(email=value):
            raise serializers.ValidationError(f"User with email '{value}' already exists")
        return value

    def validate(self, data: dict):
        if data.get('account_type') == 'Business' and not data.get('business_name'):
            raise serializers.ValidationError("'business_name' must be included for business accounts")
        return data


class OnboardUserSerializer(serializers.Serializer):
    idType = [
        ('nin', 'nin'),
        ('inec', 'inec'),
        ('none', 'none')
    ]
    identification_number = serializers.CharField(max_length=11, min_length=11)
    identification_type = serializers.ChoiceField(idType)
    phone = serializers.CharField(max_length=200)
    uuid = serializers.UUIDField()
    dob = serializers.DateField()


class OnboardBusinessSerializer(serializers.ModelSerializer):

    class Meta:
        model = Business
        fields = ('business_name', 'rc_number', 'onboarded', 'business_type')


class VerifySerializer(serializers.Serializer):
    rc_number = serializers.CharField(
        required=True, min_length=5, max_length=100)
    company_name = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',)


class UserDetailSerializer(serializers.ModelSerializer):

    def validate_account_type(self, value):
        if self.instance and self.instance.account_type != value:
            raise serializers.ValidationError("You can not update account type")
        return value

    def validate_loan_amount(self, value):
        if self.instance and self.instance.loan_amount != value:
            raise serializers.ValidationError("You can not update amount")
        return value

    class Meta:
        model = UserDetails
        fields = ('uuid', 'token', 'account_type', 'loan_amount', 'phone',)


class UpdateUserDetailsSerializers(serializers.ModelSerializer):
    model = UserDetails
    fields = ('uuid', 'account_type', 'phone')


class IndividualSerializer(serializers.ModelSerializer):
    settings = IndividualSettingsSerializer(read_only=True)

    class Meta:
        model = Individual
        fields = '__all__'

    def create(self, validated_data):
        individual = Individual.objects.create(**validated_data)
        IndividualSettings.objects.create(user=individual)
        return individual


class BusinessSerializer(serializers.ModelSerializer):

    settings = BusinessSettingsSerializer(read_only=True)

    class Meta:
        model = Business
        exclude = ('user',)

    def create(self, validated_data):
        business = Business.objects.create(**validated_data)
        BusinessSettings.objects.create(user=business)
        return business


class UserLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('company_name', 'email', 'address', 'emp_status',
                  'net_income', 'obiligation', 'staff_id', 'start_date')


class IndividualDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndividualDocuments
        fields = '__all__'


class BusinessDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDocument
        fields = '__all__'


class GuarantorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantor
        fields = '__all__'


class PinSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False)
    pin = serializers.CharField(max_length=4)


class PinUpdateSerializer(serializers.Serializer):
    uuid = serializers.UUIDField(required=False)
    old_pin = serializers.CharField(max_length=4)
    new_pin = serializers.CharField(max_length=4)
