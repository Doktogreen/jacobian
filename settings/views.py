from django.conf import settings
from django.shortcuts import get_object_or_404
from middleware.response import error_response, success_response
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import IndividualSettingsSerializer, BusinessSettingsSerializer
from .models import IndividualSettings, BusinessSettings
from users.models import UserDetails, User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.decorators import api_view
from .permissions import IsOwner

# class IndividualSettingsView(generics.RetrieveUpdateAPIView):
#     serializer_class = IndividualSettingsSerializer
#     queryset = IndividualSettings.objects.all()
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
    
#     def get_object(self):
#         queryset = self.get_queryset()
        
        
#         obj = get_object_or_404(queryset, user__user__uuid=self.kwargs['uuid'])
#         self.check_object_permissions(self.request, obj)
#         return obj

class BusinessSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = BusinessSettingsSerializer
    queryset = BusinessSettings.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        queryset = self.get_queryset()
        

        obj = get_object_or_404(queryset, user__user__uuid=self.kwargs['uuid'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    
@api_view(['POST'])
def create_individual_settings(request):
    user = User.objects.get(id=request.user.id)
    userdetails = UserDetails.objects.get(user=user)
    
    
    if hasattr(userdetails.individual, 'settings') is False:
        individual_settings = IndividualSettings.objects.create(user=userdetails.individual)
        individual_settings.save()
        return Response(data={"status":"successful"}, status=status.HTTP_200_OK)
    else:
        return Response(data={"status":"Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    
    
@api_view(['POST'])
def create_business_settings(request):
    user = User.objects.get(id=request.user.id)
    userdetails = UserDetails.objects.get(user=user)
    
    if hasattr(userdetails.business, 'settings') is False:
        business_settings = BusinessSettings.objects.create(user=userdetails.business)
        business_settings.save()
        return Response(data={"status":"successful"}, status=status.HTTP_200_OK)
    else:
        return Response(data={"status":"Already Exist"}, status=status.HTTP_400_BAD_REQUEST)
    
    
class IndividualSettingsView(APIView):
    def get(self, request):
        try:
            ud = UserDetails.objects.get(user=request.user)
            settings = IndividualSettings.objects.get(user=ud.individual)
        except IndividualSettings.DoesNotExist:
            settings = None
            
        serializer = IndividualSettingsSerializer(settings)   
        return success_response(data=serializer.data)  

    def put(self, request):
        ud = UserDetails.objects.get(user=request.user)
        try:
            settings = IndividualSettings.objects.get(user=ud.individual)
        except IndividualSettings.DoesNotExist:
            settings = IndividualSettings.objects.create(user=ud.individual)
            settings.save()
            return success_response(message="Settings updated successfully",)
        
        serializer = IndividualSettingsSerializer(settings, data=request.data)
        if serializer.is_valid() is not True:
            error_response(status=400, message= serializer._errors)
            
        serializer.save()
        return success_response(message="Settings updated successfully", data=serializer.data)
    
    
class BusinessSettingsView(APIView):
    def get(self, request):
        try:
            ud = UserDetails.objects.get(user=request.user)
            settings = BusinessSettings.objects.get(user=ud.business)
        except BusinessSettings.DoesNotExist:
            settings = None
            
        serializer = BusinessSettingsSerializer(settings)   
        return success_response(data=serializer.data)  

    def put(self, request):
        ud = UserDetails.objects.get(user=request.user)
        try:
            settings = BusinessSettings.objects.get(user=ud.business)
        except BusinessSettings.DoesNotExist:
            settings = BusinessSettings.objects.create(user=ud.business)
            settings.save()
            return success_response(message="Settings updated successfully",)
        
        serializer = BusinessSettingsSerializer(settings, data=request.data)
        if serializer.is_valid() is not True:
            error_response(status=400, message= serializer._errors)
            
        serializer.save()
        return success_response(message="Settings updated successfully", data=serializer.data)
        
        