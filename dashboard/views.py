from rest_framework import viewsets
from .models import Register_Client, Balance, Identity, Income
from .serializers import (ClientRegistrationSerializer, BalanceSerializer, IdentitySerializer,
                          IncomeSerializer, TransactionSerializer)
from datetime import datetime, date, timedelta
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from wallet.models import WitMono
from django.shortcuts import render, get_object_or_404
from users.models import UserDetails
from decouple import config
from rest_framework.response import Response
import  requests
import json
from transaction.models import Transaction
from middleware.response import *

# Create your views here.
class ClientRegistrationViewSet(viewsets.ModelViewSet):
    queryset = Register_Client.objects.all()
    serializer_class = ClientRegistrationSerializer
    lookup_field = 'customer_id'


class BalanceViewSet(viewsets.ModelViewSet):
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    lookup_field = 'customer_id'


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    lookup_field = 'customer_id'


class IdentityViewSet(viewsets.ModelViewSet):
    queryset = Identity.objects.all()
    serializer_class = IdentitySerializer
    lookup_field = 'customer_id'


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    lookup_field = 'customer_id'

class BankChartViewSet(viewsets.ModelViewSet):
    queryset = WitMono.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def list(self, request, uuid_id):
        user = get_object_or_404(UserDetails, uuid=uuid_id)
        queryset = WitMono.objects.filter(uuid=user).values_list("code")
        code = queryset[0]
        id = ''.join(code)
        headers = {
        'mono-sec-key': config("MONO_LIVE_KEY"),
        'Content-Type': 'application/json'
    }
        today = datetime.today()
        income = []
        expense = []
        # get date  strings
        last_day_of_prev_month = date.today().replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = date.today().replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        subsequent_end_month = start_day_of_prev_month - timedelta(days=1)
        subsequent_start_month = start_day_of_prev_month - timedelta(days=subsequent_end_month.day)
       
        for x in range(6):
            # if x == 0: 
            # end = datetime(last_day_of_prev_month.day, last_day_of_prev_month.month, last_day_of_prev_month.year).date()
            end = datetime.strptime("{}".format(last_day_of_prev_month), '%Y-%m-%d').strftime('%d-%m-%Y')
            start = datetime.strptime("{}".format(start_day_of_prev_month), '%Y-%m-%d').strftime('%d-%m-%Y')
            print(end)
            print(start)
            url1 = f"{config('BASEURL_MONO')}/accounts/{id}/transactions?start={start}&end={end}&type=debit"
            url2 = f"{config('BASEURL_MONO')}/accounts/{id}/transactions?start={start}&end={end}&type=credit"
            response1 = requests.get(url1, headers=headers)
            body = json.loads(response1.content)['data']
            exp_list = []
            for x in body:
                exp_list.append(x.get('amount'))
            expense.append({'month': "{}".format(last_day_of_prev_month.month), 'amount': sum(exp_list)/100})
            response2 = requests.get(url2, headers=headers)
            body = json.loads(response2.content)['data']
            income_list = []
            for x in body:
                income_list.append(x.get('amount'))
            income.append({'month': "{}".format(last_day_of_prev_month.month), 'amount': sum(income_list)/100})
            last_day_of_prev_month -= timedelta(weeks=5)
            start_day_of_prev_month -= timedelta(weeks=5)
        return Response({"message": [income, expense]})

class WalletPieChartViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def list(self, request, uuid_id):
        user = get_object_or_404(UserDetails, uuid=uuid_id)
        income_queryset = Transaction.objects.filter(user=user).filter(type="credit").values_list("amount", flat=True)
        expense_queryset = Transaction.objects.filter(user=user).filter(type="debit").values_list("amount", flat=True)
        income = []
        expense = []
        for x in income_queryset:
            income.append(float(x))
        for y in expense_queryset:
            expense.append(float(y))
        return Response({"message": [income, expense]})
                # response = requests.get(url, headers=headers)

class WalletCategoryViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def list(self, request, uuid_id):
        user = get_object_or_404(UserDetails, uuid=uuid_id)
        queryset = Transaction.objects.filter(user=user)
        FundTransfer = queryset.filter(transaction_type = "Top-Up").count()
        LoanRepay = queryset.filter(transaction_type = "loan-repayment").count()
        LoanDeposit = queryset.filter(transaction_type = "loan").count()
        Payout = queryset.filter(transaction_type = "Bank-Transfer").count()
        # Investment = queryset.filter(transaction_type = "Bank-Transfer").count()
        return Response({"message": [{
            "Wallet Fund": FundTransfer,
            "Loan Deposit": LoanDeposit,
            "Loan Repayment": LoanRepay,
            "Payout": Payout
        }]})
        # print(response.text)
        # transaction = json.loads(response.content)
        # return Response({"message": transaction})
