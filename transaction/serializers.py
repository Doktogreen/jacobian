from rest_framework.serializers import *
from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ('user', 'id')
