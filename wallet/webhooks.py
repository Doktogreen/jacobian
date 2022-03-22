import json
import hashlib
import requests
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.utils import timezone
from .models import ReservedAccounts, Wallet, AccountTransaction
from rest_framework.views import APIView
from transaction.models import Transaction
from users.models import UserDetails
from decouple import config
from django.contrib.auth.models import User

clientSecret = config("MONNIFY_SECRET")


def updateBalance(old, addition):
    new = float(old) + float(addition)
    return new


@api_view(['POST', 'GET'])
def transactionHook(request):
    body = json.loads(request.body)
    transactionHash = body["transactionHash"]
    paymentReference = body["paymentReference"]
    amount = body["amountPaid"]
    date = body["paidOn"]
    accReference = body["product"]["reference"]
    relatedAccount = ReservedAccounts.objects.get(accountReference=accReference)
    relatedUser = relatedAccount.user
    user = User.objects.get(email=relatedUser)
    ud = UserDetails.objects.get(user=user)
    print(ud)
    transactionReference = body["transactionReference"]
    bb = "{}|{}|{}|{}|{}".format(clientSecret, paymentReference, amount, date, transactionReference)
    cbytes = bb.encode('utf-8')
    hasher = hashlib.sha512(cbytes)
    hashValue = hasher.hexdigest()
    # if transactionHash == hashValue:
    # Extra Layer of verification
    Transaction.objects.create(amount=float(body["amountPaid"]),
     status='SUCCESS',  
     transaction_type=body["paymentMethod"],
        reference=transactionReference,
        type='credit', 
        user=relatedUser,
        customer_name=ud.user.first_name+' '+ud.user.last_name,
        customer_email=ud.user.email,
        narration='Fund Wallet Transaction' + ' '+ud.user.first_name+' '+ud.user.last_name, 
        currency='NGN')
    newWallet = float(ud.wallet.balance) + float(body["amountPaid"])
    print(newWallet)
    ud.wallet.balance = newWallet
    ud.save()
    AccountTransaction.objects.create(account=relatedAccount,
                                      amount=float(body["amountPaid"]),
                                      createdOn=body["paidOn"], completed=True,
                                      paymentMethod=body["paymentMethod"],
                                      providerCode=body["accountDetails"]["bankCode"],
                                      paymentReference=paymentReference,
                                      transactionReference=transactionReference,
                                      payableAmount=body["settlementAmount"])

    if Wallet.objects.filter(user=relatedUser).exists():
        print("exists")
        userWallet = Wallet.objects.get(user=relatedUser)
        increment = float(body["amountPaid"])
        currBalance = userWallet.balance
        userWallet.lastBalance = currBalance
        userWallet.balance = updateBalance(currBalance, increment)
        userWallet.status = "ACTIVE"
        userWallet.updatedAt = timezone.now()
        userWallet.save()
    else:
        increment = float(body["amountPaid"])
        Wallet.objects.create(user=relatedUser, balance=increment, lastBalance=0.0, status="ACTIVE")
    return HttpResponse("Success")

    """
    else:
        return HttpResponse("Duplicate")
    return HttpResponse("Finished")
    
    """

    """
        loginToken = authenticate()
        verificationResponse = requests.get(
            url="https://api.monnify.com/api/v2/transactions/{}".format(transactionReference),
            headers={
                "Authorization": "Bearer {}".format(loginToken)
            })
        jsonResponse = verificationResponse.json()
        print(loginToken)
        print(verificationResponse.status_code)
        print(verificationResponse)
        if verificationResponse.status_code == 200:
            if jsonResponse["responseBody"]["paymentStatus"] == "PAID":
                else:
            print("Duplicate Transaction")
            return HttpResponse("Duplicate Transaction")
            """
