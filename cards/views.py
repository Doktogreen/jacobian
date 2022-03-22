# pylint: disable=missing-module-docstring
# from django.shortcuts import render
import hashlib
import hmac
import base64
import json
from cards.serializers import CardSerializer
from middleware.response import success_response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Card
from wallet.models import Wallet
from transaction.models import Transaction
from users.models import UserDetails
from django.contrib.auth.models import User
from wallet.utils import CARD_TERMINAL_TYPES
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist



# Create your views here.
def validate_mac(*args):
    '''
    VALIDATE MAC HASH FOR EVERY TRANSACTION
    '''
    private_key = b'RR,ZQjie|mCFBkpYd%A5VjS.K.SJFuq&NlSdkPvIuv<1#38M,5YB.%Wf9P^szxVm>0w|VVCMaBQoPM|cPUcBLkTW3GvVks|o*|2I5w>q3yIFUu7b<SKqhAr2jc$S7&S2HGdz3<iBWmXRd<LGZU5d8nlP&Hf>LS5wQ8t>.Ag,&ZHYdbbmjfLnvBlB|A11jQw%PB1Zcqv7sloC;c&lpciHZZ3j8&7Pa&KCm9u.ng!3mZ4SwfO#Zy39<#V,xcsXNpMn'
    new_data = (''.join(w) for w in args)
    body = ''.join(map(str, new_data))
    digest = hmac.new(private_key,
              msg=body.encode('utf-8'),
              digestmod=hashlib.sha512
             ).hexdigest()
    token = digest
    # token = hashlib.sha512(digest.encode()).hexdigest()
    return token

def validate_response(*args):
    '''
    VALIDATE MAC HASH FOR EVERY TRANSACTION
    '''
    private_key = b'RR,ZQjie|mCFBkpYd%A5VjS.K.SJFuq&NlSdkPvIuv<1#38M,5YB.%Wf9P^szxVm>0w|VVCMaBQoPM|cPUcBLkTW3GvVks|o*|2I5w>q3yIFUu7b<SKqhAr2jc$S7&S2HGdz3<iBWmXRd<LGZU5d8nlP&Hf>LS5wQ8t>.Ag,&ZHYdbbmjfLnvBlB|A11jQw%PB1Zcqv7sloC;c&lpciHZZ3j8&7Pa&KCm9u.ng!3mZ4SwfO#Zy39<#V,xcsXNpMn'
    new_data = (''.join(w) for w in args)
    body = ''.join(map(str, new_data))
    digest = hmac.new(private_key,
              msg=body.encode('utf-8'),
              digestmod=hashlib.sha512
             ).digest()
    token = base64.b64encode(digest).decode("utf-8")
    return token

@api_view(['POST'])
def debit(request):
    '''
    THIS FUNCTION IS USED TO PROCESS DEBIT TRANSACTIONS
    '''
    body = json.loads(request.body)
    token = validate_mac(
        body['transactionReference'],
        body['requestId'],
        body['walletId'],
        str(body['amount']),
        body['currencyCode'])
    print(token)
    print(body['mac'])
    if token == body['mac']:
        try:
            card = Card.objects.get(reference=body['walletId'])
            ud = UserDetails.objects.get(pk=card.user.pk)
            wallet = Wallet.objects.get(user=ud)
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        wallet_balance = wallet.get_balance()
        if wallet.status == "INACTIVE":
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '45'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "45",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        user = User.objects.get(email=wallet)
        ud = UserDetails.objects.get(user=user)
        #check for duplicate transactions
        if Transaction.objects.filter(payment_reference=body['transactionReference']).exists() == True:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '94'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "94",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        else:
            new_balance = Decimal(body['amount']/100)
            
            if float(wallet_balance)<body['amount']/100:
                response_token = validate_mac(
                    body['transactionReference'],
                    body['requestId'],
                    '51'
                )
                return Response({
                    "amount": body['amount'],
                    "responseCode": "51",
                    "transactionReference": body['transactionReference'],
                    "requestId": body['requestId'],
                    "mac": response_token
                })
            
            if wallet.check_limit(new_balance, 'withdraw'):
                response_token = validate_mac(
                    body['transactionReference'],
                    body['requestId'],
                    '61'
                )
                return Response({
                    "amount": body['amount'],
                    "responseCode": "61",
                    "transactionReference": body['transactionReference'],
                    "requestId": body['requestId'],
                    "mac": response_token
                })
            else:
                new_balance = body['amount']/100
                wallet.withdraw(new_balance, status='SUCCESS', transaction_type = "Debit Card", payment_reference=body['transactionReference'], payment_response=CARD_TERMINAL_TYPES[body['terminalType']])
                response_token = validate_mac(
                    body['transactionReference'],
                    body['requestId'],
                    '00'
                )
                return Response({
                    "amount": body['amount'],
                    "responseCode": "00",
                    "transactionReference": body['transactionReference'],
                    "requestId": body['requestId'],
                    "mac": response_token
                })
    else:
        # Do not honor transaction
        response_token = validate_mac(
            body['transactionReference'],
            body['requestId'],
            '12'
        )
        return Response({
            "amount": body['amount'],
            "responseCode": "12",
            "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })

@api_view(['POST'])
def reversal(request):
    '''
    THIS FUNCTION IS USED TO PROCESS DEBIT TRANSACTIONS
    '''
    body = json.loads(request.body)
    token = validate_mac(
        body['transactionReference'],
        body['originalTransactionReference'],
        body['requestId'],
        body['walletId'],
        str(body['amount']),
        body['currencyCode'])
    if token == body['mac']:
        #Proceed with the transaction request
        if Transaction.objects.filter(payment_reference=body['originalTransactionReference']).exists() == False:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "originalTransactionReference": body['originalTransactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        try:
            card = Card.objects.get(reference=body['walletId'])
            ud = UserDetails.objects.get(pk=card.user.pk)
            wallet = Wallet.objects.get(user=ud)
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        # print(wallet.status)
        # if wallet.status == "Inactive":
        #         response_token = validate_mac(
        #         body['transactionReference'],
        #         body['requestId'],
        #         '00'
        #     )
        #     return Response({
        #         "amount": body['amount'],
        #         "responseCode": "00",
        #         "transactionReference": body['transactionReference'],
        #         "requestId": body['requestId'],
        #         "mac": response_token
        #     })
        if Transaction.objects.filter(payment_reference=body['originalTransactionReference']).exists() == True:
            f = Transaction.objects.filter(payment_reference=body['originalTransactionReference']).values_list('type')
            for i in f:
                print(i)
                if i[0] == 'credit':
                    response_token = validate_mac(
                        body['transactionReference'],
                        body['requestId'],
                        '94'
                    )
                    return Response({
                        "amount": body['amount'],
                        "responseCode": "94",
                        "transactionReference": body['transactionReference'],
                        "originalTransactionReference": body['originalTransactionReference'],
                        "requestId": body['requestId'],
                        "mac": response_token
                        })
        user = User.objects.get(email=wallet)
        ud = UserDetails.objects.get(user=user)
        new_balance = body['amount']/100
        wallet.deposit(new_balance, status='SUCCESS', transaction_type = "Debit Card", payment_reference=body['originalTransactionReference'], payment_response=CARD_TERMINAL_TYPES[body['terminalType']])
        response_token = validate_mac(
            body['transactionReference'],
            body['requestId'],
            '00'
        )
        return Response({
            "amount": body['amount'],
            "responseCode": "00",
            "transactionReference": body['transactionReference'],
            "originalTransactionReference": body['originalTransactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })
    else:
        # Do not honor transaction
        response_token = validate_mac(
            body['transactionReference'],
            body['requestId'],
            '12'
        )
        return Response({
            "amount": body['amount'],
            "responseCode": "12",
            "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })

@api_view(['POST'])
def enquiry(request):
    '''
    Check customer balance enquiry
    '''
    body = json.loads(request.body)
    token = validate_mac(
        body['transactionReference'],
        body['requestId'],
        body['walletId'])
    if token == body['mac']:
        try:
            card = Card.objects.get(reference=body['walletId'])
            ud = UserDetails.objects.get(pk=card.user.pk)
            wallet = Wallet.objects.get(user=ud)
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                "0",
                "",
                '25'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        if wallet.status == "INACTIVE":
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                "0",
                "",
                '45'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "45",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        wallet_balance = wallet.get_balance()
        user = User.objects.get(email=wallet)
        ud = UserDetails.objects.get(user=user)
        response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                str(int(wallet_balance)*100),
                f'{ud.user.first_name} {ud.user.last_name}',
                '00'
            )
        return Response({
            "amount": int(wallet_balance)*100,
            "name": f'{ud.user.first_name} {ud.user.last_name}',
            "responseCode": "00",
            "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })
    response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                "0",
                "",
                '12'
            )
    return Response({
        "amount": 0,
        "name": "",
        "responseCode": "12",
        "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })

@api_view(['POST'])
def place_lien(request):
    '''
    Check customer balance enquiry
    '''
    body = json.loads(request.body)
    token = validate_mac(
        body['transactionReference'],
        body['requestId'],
        body['walletId'],
        str(body['amount']),
        body['currencyCode'])
    if token == body['mac']:
        if body['amount'] > 1000000000 or body['amount'] == 0 :
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '13'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "13",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
            
        try:
            card = Card.objects.get(reference=body['walletId'])
            ud = UserDetails.objects.get(pk=card.user.pk)
            wallet = Wallet.objects.get(user=ud)
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        
        if Transaction.objects.filter(payment_reference=body['transactionReference']).exists() == True:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '94'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "94",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        
        wallet_balance = wallet.get_balance()
        
        if float(wallet_balance)<body['amount']:
            wallet.pending(body['amount'], transaction_type = "Debit Card Lien", payment_reference=body['transactionReference'], payment_response='Debit Card Lien', status='SPV')
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '51'
            )
            return Response({
                "amount": body['amount'],
                "responseCode": "51",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        user = User.objects.get(email=wallet)
        ud = UserDetails.objects.get(user=user)
        new_balance = body['amount']/100
        wallet.withdraw(new_balance, transaction_type = "Debit Card Lien", payment_reference=body['transactionReference'], payment_response='Debit Card Lien', status='SPV')
        response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '00'
            )
        return Response({
            "amount": body['amount'],
            "responseCode": "00",
            "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })
    response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '12'
            )
    return Response({
        "amount": body['amount'],
        "responseCode": "12",
        "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })

@api_view(['POST'])
def debit_lien(request):
    '''
    Check customer balance enquiry
    '''
    body = json.loads(request.body)
    token = validate_mac(
        body['transactionReference'],
        body['requestId'],
        body['walletId'],
        str(body['amount']),
        body['currencyCode']
    )
    if token == body['mac']:
        if Transaction.objects.filter(payment_reference=body['transactionReference']).exists() == True:
            f = Transaction.objects.filter(payment_reference=body['transactionReference']).values_list('status')
            
            for i in f:
                if i[0] == 'SUCCESS':
                    response_token = validate_mac(
                        body['transactionReference'],
                        body['requestId'],
                        '94'
                    )
                    return Response({
                        "amount": body['amount'],
                        "responseCode": "94",
                        "transactionReference": body['transactionReference'],
                        "requestId": body['requestId'],
                        "mac": response_token
                    })
        try:
            card = Card.objects.get(reference=body['walletId'])
            ud = UserDetails.objects.get(pk=card.user.pk)
            wallet = Wallet.objects.get(user=ud)
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        try:
            transaction = Transaction.objects.get(payment_reference=body['transactionReference'])
        except:
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '25'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "25",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        wallet_balance = wallet.get_balance()
        
        if float(wallet_balance)< body['amount']/100:
            response_token = validate_mac(
                    body['transactionReference'],
                    body['requestId'],
                    '51'
                )
            return Response({
                    "amount": body['amount'],
                    "responseCode": "51",
                    "transactionReference": body['transactionReference'],
                    "requestId": body['requestId'],
                    "mac": response_token
                })
        
        if body['amount']/100 > int(transaction.amount):
            response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '00'
            )
            return Response({
                "amount": 0,
                "name": "",
                "responseCode": "00",
                "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })
        
        transaction.status="SUCCESS"
        transaction.save()
        response_token = validate_mac(
                body['transactionReference'],
                body['requestId'],
                '00'
            )
        return Response({
            "amount": body['amount'],
            "responseCode": "00",
            "transactionReference": body['transactionReference'],
            "requestId": body['requestId'],
            "mac": response_token
        })
             
        # # else:
        # response_token = validate_mac(
        #         body['transactionReference'],
        #         body['requestId'],
        #         '05'
        #     )
        # return Response({
        #     "amount": body['amount'],
        #     "responseCode": "05",
        #     "transactionReference": body['transactionReference'],
        #     "requestId": body['requestId'],
        #     "mac": response_token
        # })
    else:
        response_token = validate_mac(
                    body['transactionReference'],
                    body['requestId'],
                    '12'
                )
        return Response({
            "amount": body['amount'],
            "responseCode": "12",
            "transactionReference": body['transactionReference'],
                "requestId": body['requestId'],
                "mac": response_token
            })


@api_view(['GET'])
def health(request):
    return Response({
        "status": "up"
    })
    
    
class CardView(APIView):
    
    def get(self, request, *args, **kwargs):
        ud = UserDetails.objects.get(user=self.request.user)
        queryset = Card.objects.filter(user=ud)
        serializer = CardSerializer(queryset, many=True)
        return success_response(data=serializer.data, message='card list')
    
    def post(self, request, *args, **kwargs):
        ud = UserDetails.objects.get(user=self.request.user)
        try:
            id = int(Card.objects.latest('id').id) + 1
        except ObjectDoesNotExist:
            id = 1
        card, created = Card.objects.get_or_create(
                        user=ud,
                        defaults={'reference': str(id).zfill(10)},
                    )
        if created:
            serializer = CardSerializer(card)
            return success_response(data=serializer.data, status=201)
        serializer = CardSerializer(card)
        return success_response(data=serializer.data, status=201)