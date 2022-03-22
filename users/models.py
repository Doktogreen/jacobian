import uuid
from django.db import models
from django.contrib.auth.models import User
User._meta.get_field('email')._unique = True

VERIFICATION_STATUS = [
        ('NOT VERIFIED', 'NOT VERIFIED'),
        ('VERIFIED', 'VERIFIED'),
        ('VERIFYING', 'VERIFYING')
    ]

RESET_TOKEN_STATUS = [
        ('expired', 'expired'),
        ('active', 'active')
    ]

ACCOUNT_TYPE = [
    ("Individual", "Individual"),
    ("Business", "Business")
]

class ResetPasswordToken(models.Model):
    token = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=100, choices=RESET_TOKEN_STATUS, default='expired')


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reset_token = models.OneToOneField(ResetPasswordToken, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    account_type = models.CharField(
        max_length=30, choices=ACCOUNT_TYPE, null=True)
    loan_amount = models.FloatField(default=0.0, blank=True, null=True)
    token = models.CharField(max_length=200, blank=True, null=True)
    pin = models.CharField(max_length=200, blank=True, null=True)
    bvn=models.CharField(max_length=12, null=True, blank=True)

    def get_users(self):
        users = {
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email
        }
        return users

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"




class Profile(models.Model):
    class Meta:
        abstract = True


GENDER = (
    ('Male', 'Male'),
    ('M', 'M'),
    ('m', 'm'),
    ('Female', 'Female'),
    ('F', 'F'),
    ('f', 'f'),
    ('Others', 'Others'),
)

MARRIAGE = (
    ('Married', 'Married'),
    ('Single', 'Single'),
    ('Divorced', 'Divorced'),
)

class Verifyme(models.Model):
    uuid = models.OneToOneField(UserDetails, on_delete=models.CASCADE)
    v_id = models.CharField(max_length=20,  null=True, blank=True)

    def __str__(self):
        return self.v_id

class Individual(models.Model):
    idType = [
        ('nin', 'nin'),
        ('inec', 'inec'),
        ('ibvn', 'ibvn'),
        ('frsc', 'frsc'),
        ('passport', 'passport')
    ]
    user = models.OneToOneField(UserDetails, related_name='individual', on_delete=models.CASCADE)
    identification_number = models.CharField(max_length=200, blank=True)
    identification_type = models.CharField(
        max_length=200, choices=idType, null=True, blank=True)
    photo_link = models.TextField(max_length=300000, null=True, blank=True)
    logo = models.CharField(max_length=200, blank=True, null=True)
    onboarded = models.BooleanField(default=False, null=True)
    lga = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(null=True, blank=True, max_length=500)
    state = models.CharField(max_length=150, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    crm_status = models.BooleanField(default=False, null=True)
    gender = models.CharField(max_length=30, blank=True, choices=GENDER)
    address_verification_status = models.CharField(choices=VERIFICATION_STATUS,
                                                   max_length=200, null=True, blank=True, default="NOT VERIFIED")
    city = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    highest_qualification = models.CharField(
        max_length=200, null=True, blank=True)
    crm_clientId = models.IntegerField(null=True, blank=True)
    crm_resourceId= models.IntegerField(null=True, blank=True)
    crm_savingsId= models.IntegerField(null=True, blank=True)
    filled_kyc = models.BooleanField(default=False, null=True)
    paystack_recipient_code=models.CharField(max_length=100, null=True, blank=True)

    def filled_kyc_form(self):
        print(self.filled_kyc)
        if self.filled_kyc is True:
            return True
        else:
            return False

    def get_kyc_status(self):
        kyc_score = 0
        if self.address_verification_status == 'VERIFIED':
            kyc_score += 1
        if self.crm_status is True:
            kyc_score += 1
        if self.address is not None:
            kyc_score += 1
        if self.onboarded is not None:
            kyc_score += 1
        if self.filled_kyc is not False:
            kyc_score += 1
        #check document upload
        if self.identification_number is not None:
            kyc_score += 1
        if kyc_score >= 5:
            print(kyc_score)
            return True
        else:
            print(kyc_score)
            return False

    def __str__(self):
        return self.user.user.first_name + " "+ self.user.user.last_name


class Business(models.Model):
    BusinessType = [
        ("limited_liablility", "limited_liablility"),
        ("partnership", "partnership"),
        ("sole_proprietorship", "sole_proprietorship")
    ]
    user = models.OneToOneField(UserDetails, related_name='business', on_delete=models.CASCADE)
    directors = models.IntegerField(null=True, blank=True)
    onboarded = models.BooleanField(default=False, null=True)
    shareholder1_identification_number = models.CharField(max_length=200, blank=True)
    shareholder2_identification_number = models.CharField(max_length=200, blank=True)
    logo = models.CharField(max_length=200, blank=True, null=True, default=None)
    rc_number = models.CharField(max_length=200, null=True, blank=True)
    office_address = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    company_name = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    business_type = models.CharField(
        max_length=200, blank=True, choices=BusinessType)
    other_business_type = models.CharField(max_length=200, blank=True)
    shareholder1_name = models.CharField(max_length=200, blank=True, null=True)
    shareholder1_id_type = models.CharField(
        max_length=200, blank=True, null=True)
    shareholder1_number = models.CharField(
        max_length=200, blank=True, null=True)
    shareholder1_email = models.CharField(
        max_length=200, blank=True, null=True)
    shareholder2_name = models.CharField(max_length=200, blank=True, null=True)
    shareholder2_id_type = models.CharField(
        max_length=200, blank=True, null=True)
    shareholder2_number = models.CharField(
        max_length=200, blank=True, null=True)
    shareholder2_email = models.CharField(
        max_length=200, blank=True, null=True)
    address_verification_status = models.CharField(choices=VERIFICATION_STATUS,
                                                   max_length=200, null=True, blank=True, default="NOT VERIFIED")
    def is_onboarded(self):
        score = 0
        if self.shareholder1_identification_number:
            score += 5
        if self.rc_number:
            score += 5
        if self.company_name:
            score += 5
        if self.phone:
            score += 5
        if score == 20:
            # self.onboarded = True
            return True
        else:
            return False

    def __str__(self):
        return self.user.user.first_name + " "+ self.user.user.last_name


class Director(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE)
    email = models.EmailField()
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    bvn = models.IntegerField()


class Guarantor(models.Model):
    GUARANTOR = (
        ('Family', 'Family'),
        ('Other', 'Other'),
    )

    user = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, choices=GUARANTOR)
    email = models.EmailField()
    first_name = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    bvn = models.CharField(max_length=15, blank=True, null=True)
    is_verified =models.BooleanField(default=False, blank=True)
    
    def __str__(self):
        return self.first_name + " " +self.last_name


class Employee(models.Model):
    emp_status = (
        ('employed', 'employed'),
        ('unemployed', 'unemployed'),
    )
    NET_INCOME = (
        ('50,000 - 100,000', '50,000 - 100,000'),
        ('100,000 - 200,000', '100,000 - 200,000'),
        ('200,000 - 300,000', '200,000 - 300,000'),
        ('300,000 - 400,000', '300,000 - 400,000'),
        ('400,000 - 500,000', '400,000 - 500,000'),
        ('600,000 - 700,000', '600,000 - 700,000'),
        ('800,000 - 900,000', '800,000 - 900,000'),
        ('900,000 - 1,000,000', '900,000 - 1,000,000'),
        ('1,000,000 - 2,000,000', '1,000,000 - 2,000,000'),
        ('2,000,000 - 3,000,000', '2,000,000 - 3,000,000'),
        ('3,000,000 - 4,000,000', '3,000,000 - 4,000,000'),
        ('4,000,000 - 5,000,000', '4,000,000 - 5,000,000'),
    )
    individual = models.OneToOneField(Individual, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, null=True, blank=True)
    emp_status = models.CharField(
        choices=emp_status, max_length=100, null=True, blank=True)
    staff_id = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    net_income = models.CharField(
        choices=NET_INCOME, max_length=200, null=True, blank=True)
    obiligation = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)


class NextOfKin(models.Model):
    individual = models.OneToOneField(Individual, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True, blank=True)
    address = models.TextField(null=True, max_length=500)
    email = models.CharField(
        max_length=50, blank=True, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(
        max_length=200, blank=True, null=True)
    relationship = models.CharField(
        max_length=50, blank=True, null=True)
    bvn = models.CharField(max_length=200, blank=True, null=True)

# Verifyme Address submission
class VerifyAddress(models.Model):
    v_id = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    idType = models.CharField(max_length=20, null=True, blank=True)
    idNumber = models.CharField(max_length=30, null=True, blank=True)
    middlename = models.CharField(max_length=200, null=True, blank=True)
    photo = models.CharField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=20, null=True, blank=True)
    birthdate = models.CharField(max_length=20, null=True, blank=True)
    createdAt = models.CharField(max_length=200, null=True, blank=True)
    lattitude = models.CharField(max_length=20, null=True, blank=True)
    longitude = models.CharField(max_length=20, null=True, blank=True)
    neighbor_name = models.CharField(max_length=200, null=True, blank=True)
    neighbor_phonr = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    street = models.CharField(max_length=200, null=True, blank=True)
    lga = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    uuid = models.OneToOneField(UserDetails, on_delete=models.CASCADE)

class IndividualDocuments(models.Model):
    userdetail = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True, blank=True)
    photo  = models.FileField(max_length=100, null=True, blank=True)
    identity = models.FileField(max_length=100, null=True, blank=True)
    nok_identity = models.FileField(max_length=100, null=True, blank=True)
    logo = models.FileField(max_length=100, null=True, blank=True)
    guarantor_identity = models.FileField(max_length=100, null=True, blank=True)

class BusinessDocument(models.Model):
    userdetail = models.ForeignKey(UserDetails, on_delete=models.CASCADE, null=True, blank=True)
    photo  = models.FileField(max_length=100, null=True, blank=True)
    identity = models.FileField(max_length=100, null=True, blank=True)
    logo = models.FileField(null=True, blank=True)
    cac = models.FileField(max_length=100, null=True, blank=True)
    director_one_identity = models.FileField(max_length=100, null=True, blank=True)
    director_two_identity = models.FileField(max_length=100, null=True, blank=True)