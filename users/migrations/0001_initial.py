# Generated by Django 3.0.7 on 2022-01-24 14:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('directors', models.IntegerField(blank=True, null=True)),
                ('onboarded', models.BooleanField(default=False, null=True)),
                ('shareholder1_identification_number', models.CharField(blank=True, max_length=200)),
                ('shareholder2_identification_number', models.CharField(blank=True, max_length=200)),
                ('logo', models.CharField(blank=True, default=None, max_length=200, null=True)),
                ('rc_number', models.CharField(blank=True, max_length=200, null=True)),
                ('office_address', models.CharField(blank=True, max_length=200)),
                ('state', models.CharField(blank=True, max_length=200, null=True)),
                ('company_name', models.CharField(blank=True, max_length=200)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('business_type', models.CharField(blank=True, choices=[('limited_liablility', 'limited_liablility'), ('partnership', 'partnership'), ('sole_proprietorship', 'sole_proprietorship')], max_length=200)),
                ('other_business_type', models.CharField(blank=True, max_length=200)),
                ('shareholder1_name', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder1_id_type', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder1_number', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder1_email', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder2_name', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder2_id_type', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder2_number', models.CharField(blank=True, max_length=200, null=True)),
                ('shareholder2_email', models.CharField(blank=True, max_length=200, null=True)),
                ('address_verification_status', models.CharField(blank=True, choices=[('NOT VERIFIED', 'NOT VERIFIED'), ('VERIFIED', 'VERIFIED'), ('VERIFYING', 'VERIFYING')], default='NOT VERIFIED', max_length=200, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Individual',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identification_number', models.CharField(blank=True, max_length=200)),
                ('identification_type', models.CharField(blank=True, choices=[('nin', 'nin'), ('inec', 'inec'), ('ibvn', 'ibvn'), ('frsc', 'frsc'), ('passport', 'passport')], max_length=200, null=True)),
                ('photo_link', models.TextField(blank=True, max_length=300000, null=True)),
                ('logo', models.CharField(blank=True, max_length=200, null=True)),
                ('onboarded', models.BooleanField(default=False, null=True)),
                ('lga', models.CharField(blank=True, max_length=200, null=True)),
                ('address', models.CharField(blank=True, max_length=500, null=True)),
                ('state', models.CharField(blank=True, max_length=150, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('crm_status', models.BooleanField(default=False, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('M', 'M'), ('m', 'm'), ('Female', 'Female'), ('F', 'F'), ('f', 'f'), ('Others', 'Others')], max_length=30)),
                ('address_verification_status', models.CharField(blank=True, choices=[('NOT VERIFIED', 'NOT VERIFIED'), ('VERIFIED', 'VERIFIED'), ('VERIFYING', 'VERIFYING')], default='NOT VERIFIED', max_length=200, null=True)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('postal_code', models.CharField(blank=True, max_length=50, null=True)),
                ('highest_qualification', models.CharField(blank=True, max_length=200, null=True)),
                ('crm_clientId', models.IntegerField(blank=True, null=True)),
                ('crm_resourceId', models.IntegerField(blank=True, null=True)),
                ('crm_savingsId', models.IntegerField(blank=True, null=True)),
                ('filled_kyc', models.BooleanField(default=False, null=True)),
                ('paystack_recipient_code', models.CharField(blank=True, max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResetPasswordToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(blank=True, max_length=10, null=True)),
                ('status', models.CharField(choices=[('expired', 'expired'), ('active', 'active')], default='expired', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='UserDetails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('uuid', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('account_type', models.CharField(choices=[('Individual', 'Individual'), ('Business', 'Business')], max_length=30, null=True)),
                ('loan_amount', models.FloatField(blank=True, default=0.0, null=True)),
                ('token', models.CharField(blank=True, max_length=200, null=True)),
                ('pin', models.CharField(blank=True, max_length=200, null=True)),
                ('business_name', models.CharField(blank=True, max_length=200, null=True)),
                ('bvn', models.CharField(blank=True, max_length=12, null=True)),
                ('reset_token', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.ResetPasswordToken')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Verifyme',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('v_id', models.CharField(blank=True, max_length=20, null=True)),
                ('uuid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
        migrations.CreateModel(
            name='VerifyAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('v_id', models.CharField(blank=True, max_length=20, null=True)),
                ('first_name', models.CharField(blank=True, max_length=200, null=True)),
                ('last_name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('idType', models.CharField(blank=True, max_length=20, null=True)),
                ('idNumber', models.CharField(blank=True, max_length=30, null=True)),
                ('middlename', models.CharField(blank=True, max_length=200, null=True)),
                ('photo', models.CharField(blank=True, max_length=200, null=True)),
                ('gender', models.CharField(blank=True, max_length=20, null=True)),
                ('birthdate', models.CharField(blank=True, max_length=20, null=True)),
                ('createdAt', models.CharField(blank=True, max_length=200, null=True)),
                ('lattitude', models.CharField(blank=True, max_length=20, null=True)),
                ('longitude', models.CharField(blank=True, max_length=20, null=True)),
                ('neighbor_name', models.CharField(blank=True, max_length=200, null=True)),
                ('neighbor_phonr', models.CharField(blank=True, max_length=20, null=True)),
                ('status', models.CharField(blank=True, max_length=20, null=True)),
                ('city', models.CharField(blank=True, max_length=20, null=True)),
                ('street', models.CharField(blank=True, max_length=200, null=True)),
                ('lga', models.CharField(blank=True, max_length=20, null=True)),
                ('state', models.CharField(blank=True, max_length=20, null=True)),
                ('country', models.CharField(blank=True, max_length=20, null=True)),
                ('uuid', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
        migrations.CreateModel(
            name='NextOfKin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True)),
                ('address', models.TextField(max_length=500, null=True)),
                ('email', models.CharField(blank=True, max_length=50, null=True)),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('phone', models.CharField(blank=True, max_length=200, null=True)),
                ('relationship', models.CharField(blank=True, max_length=50, null=True)),
                ('bvn', models.CharField(blank=True, max_length=200, null=True)),
                ('individual', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.Individual')),
            ],
        ),
        migrations.CreateModel(
            name='IndividualDocuments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.FileField(blank=True, null=True, upload_to='')),
                ('identity', models.FileField(blank=True, null=True, upload_to='')),
                ('nok_identity', models.FileField(blank=True, null=True, upload_to='')),
                ('logo', models.FileField(blank=True, null=True, upload_to='')),
                ('guarantor_identity', models.FileField(blank=True, null=True, upload_to='')),
                ('userdetail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
        migrations.AddField(
            model_name='individual',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='individual', to='users.UserDetails'),
        ),
        migrations.CreateModel(
            name='Guarantor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Family', 'Family'), ('Other', 'Other')], max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('bvn', models.CharField(blank=True, max_length=15, null=True)),
                ('is_verified', models.BooleanField(blank=True, default=False)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('emp_status', models.CharField(blank=True, choices=[('employed', 'employed'), ('unemployed', 'unemployed')], max_length=100, null=True)),
                ('staff_id', models.CharField(blank=True, max_length=100, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('net_income', models.CharField(blank=True, choices=[('50,000 - 100,000', '50,000 - 100,000'), ('100,000 - 200,000', '100,000 - 200,000'), ('200,000 - 300,000', '200,000 - 300,000'), ('300,000 - 400,000', '300,000 - 400,000'), ('400,000 - 500,000', '400,000 - 500,000'), ('600,000 - 700,000', '600,000 - 700,000'), ('800,000 - 900,000', '800,000 - 900,000'), ('900,000 - 1,000,000', '900,000 - 1,000,000'), ('1,000,000 - 2,000,000', '1,000,000 - 2,000,000'), ('2,000,000 - 3,000,000', '2,000,000 - 3,000,000'), ('3,000,000 - 4,000,000', '3,000,000 - 4,000,000'), ('4,000,000 - 5,000,000', '4,000,000 - 5,000,000')], max_length=200, null=True)),
                ('obiligation', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('individual', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.Individual')),
            ],
        ),
        migrations.CreateModel(
            name='Director',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(blank=True, max_length=30, null=True)),
                ('last_name', models.CharField(blank=True, max_length=30, null=True)),
                ('bvn', models.IntegerField()),
                ('business', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.Business')),
            ],
        ),
        migrations.CreateModel(
            name='BusinessDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.FileField(blank=True, null=True, upload_to='')),
                ('identity', models.FileField(blank=True, null=True, upload_to='')),
                ('logo', models.FileField(blank=True, null=True, upload_to='')),
                ('cac', models.FileField(blank=True, null=True, upload_to='')),
                ('director_one_identity', models.FileField(blank=True, null=True, upload_to='')),
                ('director_two_identity', models.FileField(blank=True, null=True, upload_to='')),
                ('userdetail', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
        migrations.AddField(
            model_name='business',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='business', to='users.UserDetails'),
        ),
    ]
