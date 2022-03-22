import json
import hashlib
import base64
from middleware.response import *
import requests
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.status import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from .serializers import InvestmentSerializer, TransferSerializer
from users.models import UserDetails
from users.serializers import PinSerializer
from loan.sign import InvestSign
from loan.models import Contract
from wallet.models import Wallet
from transaction.models import Transaction
from transaction.processor import Flutterwave
from transaction.transaction_complete_hook import TransactionCompleteHook
from transaction.utils import generate_transaction_reference
from transaction.serializers import TransactionSerializer
from datetime import date
from dateutil.relativedelta import relativedelta
from .models import Investment
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from decouple import config


@api_view(('POST',))
def check_pin(request):
    serializer = PinSerializer(data=request.data)
    if serializer.is_valid() is not True:
        return error_response(data=serializer._errors, status=400)

    data = serializer.data

    pin = hashlib.sha256(data['pin'].encode()).hexdigest()
    ud = UserDetails.objects.get(user=request.user)

    if ud.pin is None:
        return success_response(message='Please Set Pin')

    if pin != ud.pin:
        is_none = False
        return error_response(message='Invalid Pin', status=200)
    else:
        return success_response(message='Pin Successful')


@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def bank_transfer(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        serializer = TransferSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        ud = get_object_or_404(UserDetails, uuid=data['uuid'])
        get_wallet = Wallet.objects.get(user=ud)

        if get_wallet.get_balance() < data['amount']:
            return Response(
                {'message': 'Insufficent Wallet Balance', 'balance': '{}'.format(get_wallet.balance)},
                status=400)

        do_transfer = Flutterwave.transfer(
            is_test=False, account_number=data['account_number'],
            account_bank=data['account_bank'],
            amount=data['amount'],
            currency='NGN', beneficary_name=data['beneficary_name'])
        create_transaction = Transaction.objects.create(user=ud,
                                                        amount=data['amount'],
                                                        status='NEW',
                                                        type='debit',
                                                        transaction_type='Bank-Transfer',
                                                        reference=generate_transaction_reference(
                                                            type='BT'),
                                                        customer_name=data['beneficary_name'],
                                                        currency='NGN',
                                                        narration="Bank Transfer to {}".format(
                                                            data['beneficary_name'])
                                                        )
        print(do_transfer.text)
        if do_transfer == "None":
            return Response({"message": do_transfer[errMsg]})
        else:
            if do_transfer['data']['status'] == 'NEW':
                data = do_transfer['data']
                verify = Flutterwave.verify_transfer(
                    is_test=True, id=data['id'])
                print(verify)
                if verify['data']['status'] == 'PENDING':
                    # get_wallet.withdraw(data['amount'])
                    create_transaction.status = "SPV"
                    create_transaction.payment_reference = verify['data']['reference']
                    create_transaction.payment_response = verify['data']['narration']
                    create_transaction.save()
                    serializer = TransactionSerializer(create_transaction)

                    return Response({'status': 'success',
                                    'data': serializer.data}, status=HTTP_200_OK)
                else:
                    create_transaction.status = 'FAILED',
                    create_transaction.payment_reference = verify['data']['reference']
                    create_transaction.payment_response = verify['data']['narration']
                    create_transaction.save()
                    serializer = TransactionSerializer(create_transaction)
                    return Response({'status': 'failed',
                                    'data': serializer.data}, status=HTTP_200_OK)
            elif do_transfer['error'] is True:
                create_transaction.status = 'FAILED'
                create_transaction.save()
                return Response({'message': do_transfer}, status=status.HTTP_200_OK)

            elif do_transfer['data']['status'] == "FAILED":
                create_transaction.status = "FAILED"
                create_transaction.save()
                return Response({'message': do_transfer['data']['complete_message']}, status=status.HTTP_200_OK)
            else:
                create_transaction.status = "FAILED"
                create_transaction.save()
                return Response({'message': "Transaction Failed"}, status=status.HTTP_200_OK)


@api_view(('POST',))
def bank_transfer_webhook(request):
    if request.method == 'POST':
        body = json.loads(request.body)

        #
        if body["event.type"] == "Transfer":
            transaction = Transaction.objects.get(
                payment_reference=body['transfer']['reference'])

            if body['transfer']['status'] == "SUCCESS":
                debit = TransactionCompleteHook.debit(
                    transaction_id=transaction.id)
                transaction.status = 'SUCCESS'
                transaction.save()
                serializer = TransactionSerializer(transaction)
                return Response({'status': 'success',
                                 'data': serializer.data}, status=HTTP_200_OK)
            else:
                transaction.status = 'FAILED'
                transaction.save()
                serializer = TransactionSerializer(transaction)
                return Response({'status': 'failed',
                                 'data': serializer.data}, status=HTTP_200_OK)


class InvestmentView(APIView):

    def get(self, request):
        ud = UserDetails.objects.get(user=request.user)
        filter_investments = Investment.objects.filter(uuid=ud)
        serializer = InvestmentSerializer(filter_investments, many=True)
        return success_response(data=serializer.data, message="User investments")

    def post(self, request, format=None):
        ud = UserDetails.objects.get(user=request.user)
        uuid = ud.pk
        request.data.update({"uuid": uuid})
        serializer = InvestmentSerializer(data=request.data)
        if serializer.is_valid() is not True:
            return error_response(data=serializer._errors, status=400)

        data = serializer.data
        rate = 13/100
        amount = data['amount']
        duration = data['duration']
        start_date = data['start_date']
        maturity_date = date.today() + relativedelta(months=+data['duration'])
        days = maturity_date - date.today()
        interest = int(data['amount']) * int(rate) * int((days.days-1)/365)
        wht = interest*10/100
        final_amount = int(data['amount']) + int(interest) - int(wht)

        sign = InvestSign.send_signature(firstname=ud.user.first_name, lastname=ud.user.last_name, email=ud.user.email,
                                         date=date, amount=amount, payment_duration=duration, interest_due=interest,
                                         repayment_amount=final_amount)
        print(sign)

        if sign['code'] == 0:
            if sign['requests']['request_status'] == 'inprogress':
                investment = Investment.objects.create(
                    uuid=ud, status="Pending", amount=amount, rate=rate, days=days.days - 1, wht=wht,
                    total_amount=final_amount, duration=duration, maturity_date=maturity_date, start_date=start_date,
                    interest=interest)
                Contract.objects.create(
                    status="Sent",
                    name=ud.user.first_name + ' ' + ud.user.last_name,
                    email=ud.user.email,
                    mobile=ud.phone
                )
                serializer = InvestmentSerializer(investment)

                return success_response(data=serializer.data,
                                        message="Investment Created, Kindly Check Your Email to Approve")
            else:
                return error_response(status=status.HTTP_503_SERVICE_UNAVAILABLE)
        else:
            return error_response(status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(('POST',))
@permission_classes((IsAuthenticated,))
def manual_transfer(request):
    if request.method == 'POST':

        data = json.loads(request.body)
        serializer = TransferSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        ud = get_object_or_404(UserDetails, uuid=data['uuid'])
        get_wallet = Wallet.objects.get(user=ud)
        if float(get_wallet.balance) < float(data['amount']):
            return error_response(message='Insufficent Wallet Balance',
                                  data={'balance': '{}'.format(get_wallet.balance)},
                                  status=400)
        if hashlib.sha256(data['pin'].encode()).hexdigest() != ud.pin:
            return error_response(message="Transaction pin is not correct", status=200)
        new_balance = float(get_wallet.balance) - float(data['amount'])
        Wallet.objects.filter(user=ud).update(balance=new_balance)
        message = Mail(
            from_email="support@simplefinance.ng",
            to_emails='support@simplefinance.ng',
            subject='Request for bank transfer',
            html_content='''A request has been made by {0} {1} <br />
            <strong>Account Number:</strong> {2} <br />
            <strong>Account Bank:</strong>  {3}<br/>
            <strong>Amount:</strong> {4}<br/>
            <strong>Beneficiary Name:</strong> {5}<br/>
            <strong>Wallet Balance:</strong> {6}<br/>
            <strong>User Unique Identifier:</strong> {7}<br/>
            '''.format(ud.user.first_name, ud.user.last_name, data['account_number'], data['account_bank'], data['amount'], data['beneficary_name'], get_wallet.balance, data['uuid'])
        )
        try:
            sg = SendGridAPIClient(config('SENDGRID_API_KEY'))
            response = sg.send(message)

        except Exception as e:
            error_response(message="Request was not sent, please contact support to transfer the funds to you", status=200)
        return error_response(message="Request sent successfully and will be processed within 24 hours", status=200)


# BILL PAYMENT
def verifyMerchant():
    timestamp = int(time.time())
    magtipon_key = config('MAGTIPON_KEY')
    username = config('MAGTIPON_USERNAME')
    body = str(timestamp)+magtipon_key
    token = base64.b64encode(hashlib.sha512(body.encode()).digest())
    headers = {
        "Authorization": "magtipon {0}:{1}".format(username, token.decode("utf-8")),
        "timestamp": str(timestamp),
        "content-type": 'application/json'
    }
    return headers


def getSignature(RequestRef):
    magtipon_key = config('MAGTIPON_KEY')
    body = str(RequestRef)+magtipon_key
    signature = base64.b64encode(hashlib.sha512(body.encode()).digest()).decode("utf-8")
    print(signature)
    return signature


def checkAccountBalance():
    url = f"{config('MAGTIPON_URL')}/api/v1/account/balance"
    headers = verifyMerchant()
    requestData = requests.get(url, headers=headers)
    print(requestData)
    response = json.loads(requestData.content)
    print(response)
    return response.balance

# api to retrieve bill services


@csrf_exempt
@api_view(('GET',))
def getServices(request):
    headers = verifyMerchant()
    url = f"{config('MAGTIPON_URL')}/api/v1/services"
    if request.method == "GET":
        requestData = requests.get(url, headers=headers)
        print(requestData.content)
        data = json.loads(requestData.content)
        return success_response(message=data)
    else:
        return error_response(message="Method not allowed")

# api to validate bill payment


@csrf_exempt
@api_view(('POST',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validateCustomer(request):
    headers = verifyMerchant()
    url = f"{config('MAGTIPON_URL')}/api/v1/transaction/validate"
    if request.method == "POST":
        body = json.loads(request.body)
        Amount = body['Amount']
        PaymentCode = body['PaymentCode']
        CustomerId = body['CustomerId']
        request_data = json.dumps({
            "Amount": Amount,
            "PaymentCode": PaymentCode,
            "CustomerId": CustomerId
        })
        print(request_data)
        requestData = requests.post(url, data=request_data, headers=headers)
        print(requestData)
        data = json.loads(requestData.content)
        return success_response(message=data, status=status.HTTP_200_OK)
    else:
        return error_response(message="Method not allowed")

# api to make bill payment


@csrf_exempt
@api_view(('POST',))
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def makeBill(request):
    headers = verifyMerchant()
    url = f"{config('MAGTIPON_URL')}/api/v1/transaction/payment"
    if request.method == "POST":
        body = json.loads(request.body)
        uuid = body['uuid']
        ud = get_object_or_404(UserDetails, uuid=uuid)
        wallet = Wallet.objects.get(user=ud)
        Amount = Decimal(body['Amount'])
        if wallet.get_balance() < Amount:
            return error_response(message="Insufficent wallet balance", status=status.HTTP_200_OK)

        PaymentCode = body['PaymentCode']
        CustomerId = body['CustomerId']
        Fullname = body['Fullname']
        RequestRef = generate_transaction_reference()
        request_data = json.dumps({
            "Amount": body['Amount'],
            "RequestRef": RequestRef,
            "PaymentCode": PaymentCode,
            "CustomerId": CustomerId,
            "CustomerDetails": {
                "Fullname": Fullname,
                "MobilePhone": ud.phone,
                "Email": ud.user.email
            },
            "Signature": getSignature(RequestRef)
        })
        requestData = requests.post(url, data=request_data, headers=headers)
        data = json.loads(requestData.content)
        if data["ResponseCode"] == "90000":
            wallet.withdraw(Amount, transaction_type="Bill", payment_reference=RequestRef,
                            payment_response=PaymentCode, status='SUCCESS')
        return success_response(data=data, status=status.HTTP_200_OK)
    else:
        return error_response(message="Method not allowed")
