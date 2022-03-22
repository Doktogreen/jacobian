# pylint: disable=missing-module-docstring

from django.shortcuts import get_object_or_404
import http.client
import json
import hashlib
from decouple import config
from django.contrib.auth.models import User
from django.db import IntegrityError
from .models import Wallet, ReservedAccounts, WitMono
from transaction.serializers import TransactionSerializer
from transaction.models import Transaction
from transaction.utils import generate_transaction_reference
from users.models import UserDetails
from .serializers import (VerifyBankAccount, WalletSerializer, TransferToBankSerializer, GetReservedAccountSerializer,
                          WitMonoSerializer)
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework import viewsets
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from rest_framework.response import Response
from rest_framework import status
import requests
from middleware.response import response, success_response, error_response, handle_response
from decouple import config
from django.views.decorators.csrf import csrf_exempt


class TransactionSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class WalletViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Wallet.objects.all()
    # lookup_field = 'uuid'
    serializer_class = WalletSerializer

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a model instance.
        """
        instance = self.get_object()
        serializer = WalletSerializer(instance)

        return success_response(data={"wallet details": serializer.data})


class WitMonoViews(viewsets.ModelViewSet):
    '''
    Connect bank account to withmono for web app
    '''
    queryset = WitMono.objects.all()
    serializer_class = WitMonoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def list(self, request, uuid_id):
        user = get_object_or_404(UserDetails, uuid=uuid_id)
        queryset = WitMono.objects.filter(uuid=user)
        serializers = WitMonoSerializer(queryset, many=True)
        return success_response(data=serializers.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a model instance.
        """
        instance = self.get_object()
        serializer = WitMonoSerializer(instance.witmono)
        return success_response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        uuid = request.data['uuid']
        code = request.data['code']
        user = get_object_or_404(UserDetails, uuid=uuid)
        conn = http.client.HTTPSConnection(config("BASEURL_MONO")[8:])
        body1 = {
            "code": code
        }
        json_body = json.dumps(body1)
        headers = {
            'mono-sec-key': config("MONO_LIVE_KEY"),
            'Content-type': 'application/json'
        }
        conn.request("POST", "/account/auth", json_body, headers)
        res = conn.getresponse()
        data = res.read()
        resp = json.loads(data)
        print(resp)
        try:
            token = resp['id']
            WitMono.objects.create(
                uuid=user,
                code=token
            )
            return success_response(message="Connected Account Successfully")
        except KeyError:
            return response(success=False, message=f"Failed to Connect Account",
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, data=None)


@ api_view(['GET'])
def Balance(request, uuid):
    ud = UserDetails.objects.get(uuid=uuid)
    # return response(success=True, message="User Balance", data={"balance":ud.wallet.get_balance()}, status_code=status.HTTP_200_OK)
    return success_response(data=ud.wallet.get_balance(), message="wallet balance")


class TransactionViews(viewsets.ModelViewSet):
    queryset = UserDetails.objects.all()
    serializer_class = TransactionSerializer
    pagination_class = TransactionSetPagination

    def list(self, request, uuid_id):
        ud = get_object_or_404(UserDetails, uuid=uuid_id)
        transaction = Transaction.objects.filter(
            user=ud).order_by('-created_date')[:50]
        serializer = TransactionSerializer(transaction, many=True)
        wallet = Wallet.objects.get(user=ud)

        return Response(
            {'status': 'success', "wallet-balance": wallet.get_balance(),
             'Transaction-details': serializer.data},
            status=status.HTTP_200_OK)


def send_email(amount, bankName, destinationAccount, reference):
    "Send email for manual transfer request"
    subject, from_email, to = 'TRANSFER REQUEST', "admin@simplefing.com", "admin@simplefing.com"
    text_content = "hello"
    # text_content = 'Welcome to Simple Finance. We’re your one-stop hub for getting collateral-free loans with the lowest interest rates and experiencing profitable investment opportunities.'
    html_content = "<p>User with Reference " + reference + " has requested for a transfer</p> <p>Transfer amount: " + str(
        amount) + "</p> <p>Destination Account: " + str(destinationAccount) + "</p> <p>Destination Bank: " + bankName + "</p"
    # html_content = "Hello " + firstname,
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    print("about to")
    msg.send()
    print("sending")


def check_pin(user, pin):
    pin = hashlib.sha256(pin.encode()).hexdigest()
    ud = UserDetails.objects.get(user=user)

    if ud.pin is None:
        return False

    if pin != ud.pin:
        return False
    else:
        return True


@ api_view(['POST'])
def transfer_to_bank(request):
    user = User.objects.get(id=request.user.id)
    userdetails = UserDetails.objects.get(user=user)

    serializer_data = TransferToBankSerializer(data=request.data)
    serializer_data.is_valid(raise_exception=True)
    data = serializer_data.data
    wallet = Wallet.objects.get(user=userdetails)
    try:
        account = ReservedAccounts.objects.get(user=userdetails)
    except ReservedAccounts.DoesNotExist:
        return error_response(message="Reserved account not found", status=200, data=None)

    if check_pin(user, data['pin']) is False:
        return error_response(status=200, message="Invalid pin")

    if wallet.get_balance() < data['amount']:
        return error_response(message="Insufficent wallet balance", status=status.HTTP_200_OK)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJsaXZlIiwic3ViIjozODM4MywiaWF0IjoxNTg2MzAwMzA0LCJleHAiOjE1ODYzMDAzNjR9.Bj-ITOXdhEHwSzBZowlVvr1PGadLri2CrpEm0o6nxMc"
    }

    resolve_account_payload = {
        "accountNumber": data['account_number'],
        "beneficiaryBank": data['bank_code'],
        "userName": config('USERNAME_PROVIDUS'),
        "password": config('PASSWORD_PROVIDUS')
    }

    resolve_account = requests.post(f"{config('TRANSFER_BASEURL_PROVIDUS')}/GetNIPAccount",
                                    headers=headers, json=resolve_account_payload)
    resolve_account_data = resolve_account.json()
    if resolve_account_data['responseCode'] == "00":

        transferrecipient_params = {
            "beneficiaryAccountName": resolve_account_data['accountName'],
            "transactionAmount": data['amount'],
            "currencyCode": "NGN",
            "narration": "simplefi transfer",
            "sourceAccountName": account.accountName,
            "beneficiaryAccountNumber": resolve_account_data['accountNumber'],
            "beneficiaryBank": data['bank_code'],
            "transactionReference": generate_transaction_reference(),
            "userName": config('USERNAME_PROVIDUS'),
            "password": config('PASSWORD_PROVIDUS')
        }

        transfer = requests.post(f"{config('TRANSFER_BASEURL_PROVIDUS')}/NIPFundTransfer",
                                 json=transferrecipient_params, headers=headers)
        print(transfer.json())
        if transfer.status_code == 200:
            transfer_data = transfer.json()
            if transfer_data['responseCode'] == "00":
                wallet.withdraw(data['amount'],
                                status='SUCCESS', transaction_type="Bank Transfer",
                                payment_reference=transfer_data['sessionId'],
                                payment_response=transfer_data['responseMessage'])
                return success_response(message='Transfer successful', status=status.HTTP_200_OK)
            elif transfer_data['responseCode'] == "pending":
                wallet.withdraw(data['amount'])
                return success_response(message='Success pending validation', status=status.HTTP_200_OK)
            elif transfer_data['responseCode'] == "otp":
                transaction = Transaction.objects.create(
                    user=userdetails,
                    transaction_type='Bank-Transfer',
                    status='SPV',
                    amount=data['amount'],
                    type='debit',
                    payment_reference=transfer_data['data']['reference'],
                    currency='NGN'
                )
                transaction.save()
                return success_response(message='success pending otp validation', status=status.HTTP_200_OK)
            elif transfer_data['responseCode'] == "32":
                transaction = Transaction.objects.create(
                    user=userdetails,
                    transaction_type='Bank-Transfer',
                    status='FAILED',
                    amount=data['amount'],
                    type='debit',
                    payment_reference=transfer_data['sessionId'],
                    payment_response=transfer_data['responseMessage'],
                    currency='NGN'
                )
                transaction.save()
                return error_response(message='Transaction Failed', status=status.HTTP_200_OK)
        else:
            return error_response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        return error_response(message="Account number could not be resolved", status=status.HTTP_200_OK)


@api_view(['POST'])
def fund_wallet(request):
    body = json.loads(request.body)
    if 'sdk' in body:
        print(body)
        ud = UserDetails.objects.get(uuid=body['uuid'])
        wallet = Wallet.objects.get(user=ud)
        wallet.deposit(
            body['amount'],
            transaction_type='Top-Up', status=body['status'],
            payment_reference=body['payment_reference'])
        return success_response(message="Wallet funding successful")
    else:
        return error_response(message="sdk required", status=status.HTTP_400_BAD_REQUEST)


class FundWallet(APIView):
    def post(self, request, *args, **kwargs):
        body = json.loads(request.body)
        if 'sdk' in body:
            print(body)
            ud = UserDetails.objects.get(uuid=body['uuid'])
            wallet = Wallet.objects.get(user=ud)
            wallet.deposit(
                body['amount'],
                transaction_type='Top-Up', status=body['status'],
                payment_reference=body['payment_reference'],
                payment_response=body['narration'])
            return success_response(message="wallet funding successful")
        else:
            return error_response(status=status.HTTP_400_BAD_REQUEST)


'''Virtual Accounts'''


@csrf_exempt
@api_view(['GET'])
def getbanks(request):
    '''
    GET A LIST OF ALL NIP BANKS
    '''
    banks = requests.get(f'{config("TRANSFER_BASEURL_PROVIDUS")}/GetNIPBanks')
    return success_response(data=json.loads(banks.content))


# def providusdevAuthentication():
#     return {
#         'base_url': "http://154.113.16.142:8088/appdevapi/api/",
#         'Client-Id': "dGVzdF9Qcm92aWR1cw==",
#         'X-Auth-Signature': 'BE09BEE831CF262226B426E39BD1092AF84DC63076D4174FAC78A2261F9A3D6E59744983B8326B69CDF2963FE314DFC89635CFA37A40596508DD6EAAB09402C7'
#     }


def providusAuthentication():
    secret_key = config('CLIENTID_PROVIDUS')+":"+config("SECRET_PROVIDUS")
    return {
        'base_url': config('BASEURL_PROVIDUS'),
        'Client-Id': config("CLIENTID_PROVIDUS"),
        'X-Auth-Signature': hashlib.sha512(secret_key.encode()).hexdigest()
    }


@ api_view(['POST'])
def createAccount(request, uuid):
    '''
    CREATE A VIRTUAL ACCOUNT
    '''
    body = json.loads(request.body)
    user = get_object_or_404(UserDetails, uuid=uuid)
    first_name = user.user.first_name
    last_name = user.user.last_name
    account_name = first_name + " " + last_name
    bvn = body['bvn']
    data = json.dumps({
        "account_name": account_name,
        "bvn": bvn
    })
    createRequest = requests.post(
        providusAuthentication()['base_url']+"PiPCreateReservedAccountNumber",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Client-Id": providusAuthentication()['Client-Id'],
            "X-Auth-Signature": providusAuthentication()['X-Auth-Signature']
        })
    response = json.loads(createRequest.content)
    print(response)
    try:
        ReservedAccounts.objects.create(
            user=user,
            accountName=response['account_name'],
            accountNumber=response['account_number'],
            bankCode="000023",
            bankName="Providus Bank"
        )
    except IntegrityError:
        return error_response(status=200, message='Reserved account already exist')

    return success_response(message='Reserved account created')


@api_view(["GET"])
def getReservedAccount(request, uuid):
    '''
    Get a user's reserved account
    '''
    try:
        user = get_object_or_404(UserDetails, uuid=uuid)
    except:
        return success_response(message="Reserved account not found")
    reservedAccount = ReservedAccounts.objects.get(user=user)
    serialized_data = GetReservedAccountSerializer(reservedAccount)
    return success_response(message="Reserved account details", data=serialized_data.data)


@api_view(['POST'])
def reservedAccountWebhook(request):
    '''
    Webhook url called whenever a reserved account is credited
    '''
    header = request.META
    body = json.loads(request.body)
    secret_key = config('CLIENTID_PROVIDUS')+":"+config("SECRET_PROVIDUS")
    try:
        if header['HTTP_X_AUTH_SIGNATURE'] == hashlib.sha512(secret_key.encode()).hexdigest():
            accountNumber = body['accountNumber']
            account = ReservedAccounts.objects.get(accountNumber=accountNumber)
            user = account.user
            verifyTransaction = requests.get(
                providusAuthentication()[
                    'base_url']+'PiPverifyTransaction_settlementid?settlement_id={}'.format(body['settlementId'])
            )
            if json.loads(verifyTransaction.content)['settlementId'] != body['settlementId']:
                try:
                    transaction = get_object_or_404(
                        Transaction, payment_reference=body['settlementId'])
                    print(transaction)
                    return Response({
                        "requestSuccessful": True,
                        "sessionId":  body['sessionId'],
                        "responseMessage": "duplicate transaction",
                        "responseCode": "01"
                    })
                except:
                    wallet = user.wallet
                    wallet.deposit(float(body['settledAmount']),
                                   status='SUCCESS', payment_reference=body['settlementId'] + " " +
                                   body['sourceAccountNumber'] + " " + body['sourceBankName'])
                    return Response({
                        "requestSuccessful": True,
                        "sessionId": body['sessionId'],
                        "responseMessage": "success",
                        "responseCode": "00"
                    })
            else:
                return Response({
                    "requestSuccessful": True,
                    "sessionId": body['sessionId'],
                    "responseMessage": "rejected transaction",
                    "responseCode": "02"
                })
        else:
            return Response({
                "requestSuccessful": True,
                "sessionId": body['sessionId'],
                "responseMessage": "rejected transaction",
                "responseCode": "02"
            })
    except KeyError as e:
        return Response({
            "requestSuccessful": True,
            "sessionId": body['sessionId'],
            "responseMessage": "rejected transaction",
            "responseCode": "02"
        })


'''Virtual Accounts Ends'''


@ api_view(['POST'])
def verify_bankaccount(request):

    serializer = VerifyBankAccount(data=request.data)
    serializer.is_valid(raise_exception=True)
    body = serializer.data
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJlbnYiOiJsaXZlIiwic3ViIjozODM4MywiaWF0IjoxNTg2MzAwMzA0LCJleHAiOjE1ODYzMDAzNjR9.Bj-ITOXdhEHwSzBZowlVvr1PGadLri2CrpEm0o6nxMc"
    }

    resolve_account_payload = {
        "accountNumber": body['account_number'],
        "beneficiaryBank": body['bank_code'],
        "userName": "test",
        "password": "test"
    }

    resolve_account = requests.post(f"{config('TRANSFER_BASEURL_PROVIDUS')}/GetNIPAccount",
                                    headers=headers, json=resolve_account_payload)
    resolve_account_data = resolve_account.json()
    return success_response(data=resolve_account_data)
