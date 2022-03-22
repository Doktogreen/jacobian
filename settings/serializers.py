from rest_framework import serializers
from .models import IndividualSettings, BusinessSettings


class IndividualSettingsSerializer(serializers.ModelSerializer):

    user = serializers.ReadOnlyField(source='user.pk')
    class Meta:
        model = IndividualSettings
        fields = '__all__'
        

class BusinessSettingsSerializer(serializers.ModelSerializer):
    
    user = serializers.ReadOnlyField(source='user.pk')
    class Meta:
        model = BusinessSettings
        fields = '__all__'
