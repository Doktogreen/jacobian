# Generated by Django 3.0.7 on 2022-01-24 14:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Investment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(blank=True, default=0.0, null=True)),
                ('rate', models.FloatField(blank=True, default=0.0, null=True)),
                ('days', models.IntegerField(blank=True, null=True)),
                ('wht', models.FloatField(blank=True, default=10.0, null=True)),
                ('total_amount', models.FloatField(blank=True, default=0.0, null=True)),
                ('duration', models.IntegerField(blank=True, null=True)),
                ('maturity_date', models.DateField(blank=True, null=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('interest', models.FloatField(blank=True, default=10.0, null=True)),
                ('status', models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied'), ('Completed', 'Completed')], max_length=90, null=True)),
                ('currency', models.CharField(blank=True, choices=[('NGN', 'NGN')], default='NGN', max_length=90, null=True)),
                ('contract_status', models.CharField(blank=True, choices=[('Sent', 'Sent'), ('Withdrawn', 'Withdrawn'), ('Denied', 'Denied'), ('Approved', 'Approved')], max_length=90, null=True)),
                ('uuid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UserDetails')),
            ],
        ),
    ]
