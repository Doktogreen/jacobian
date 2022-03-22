from rest_framework.views import *
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from .models import *
from wallet.models import WitMono
import requests
import json
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from decouple import config
from middleware.response import response as rs

# Create your views here.

class BankTransactions(viewsets.ModelViewSet):
    queryset = WitMono.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def list(self, request, uuid_id):
        user = get_object_or_404(UserDetails, uuid=uuid_id)
        try:
            queryset = WitMono.objects.filter(uuid=user).values_list("code")
            code = queryset[0]
            id = ''.join(code)
            headers = {
            'mono-sec-key': config("MONO_LIVE_KEY"),
            'Content-Type': 'application/json'
        }
            url = "https://api.withmono.com/accounts/{}/transactions".format(id)

            response = requests.get(url, headers=headers)
            transaction = json.loads(response.content)
            return Response({"message": transaction}, status=status.HTTP_200_OK)
        except:
            return rs(data=None, success = False, message="user account not connected", status_code = status.HTTP_200_OK)
