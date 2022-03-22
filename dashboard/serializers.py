from rest_framework import serializers
from .models import Register_Client, Balance, Identity, Income, Transaction

class ClientRegistrationSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dashboard:register_client-detail", lookup_field="customer_id")
    class Meta:
        model = Register_Client
        fields = [ 'id', 'url','customer_id', 'validated', 'bank_id']

class BalanceSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dashboard:check_balance-detail", lookup_field="customer_id")
    customer_id = serializers.HyperlinkedRelatedField(view_name='dashboard:register_client-detail', 
                                                queryset=Register_Client.objects,
                                                many=True, lookup_field="customer_id")
    class Meta:
        model = Balance
        fields = '__all__'

class IncomeSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dashboard:check_balance-detail", lookup_field="customer_id")
    customer_id = serializers.HyperlinkedRelatedField(view_name='dashboard:register_client-detail', 
                                                queryset=Register_Client.objects,
                                                many=True, lookup_field="customer_id")
    class Meta:
        model = Income
        fields = '__all__'

class IdentitySerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dashboard:check_balance-detail", lookup_field="customer_id")
    customer_id = serializers.HyperlinkedRelatedField(view_name='dashboard:register_client-detail', 
                                                queryset=Register_Client.objects,
                                                many=True, lookup_field="customer_id")
    class Meta:
        model = Identity
        fields = '__all__'

class TransactionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="dashboard:check_balance-detail", lookup_field="customer_id")
    customer_id = serializers.HyperlinkedRelatedField(view_name='dashboard:register_client-detail', 
                                                queryset=Register_Client.objects,
                                                many=True, lookup_field="customer_id")
    class Meta:
        model = Transaction
        fields = '__all__'
