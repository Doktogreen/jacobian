import random
import string
import requests
from rave_python import Rave, Misc, RaveExceptions
from decouple import config
from .models import Transaction
from wallet.models import Wallet
from users.models import User, UserDetails


def test_check(is_test):
    if is_test:
        publickey = config('RAVE_PUBLIC_KEY_TEST')
        secretkey = config('RAVE_SECRET_KEY_TEST')
        production = False
        usingEnv = False
    else:
        publickey = config('RAVE_PUBLIC_KEY')
        secretkey = config('RAVE_SECRET_KEY')
        production = False
        usingEnv = False

    return Rave(publicKey=publickey, secretKey=secretkey,
                production=production, usingEnv=usingEnv)


class Flutterwave:

    @staticmethod
    def initialize(is_test, uuid, card_number, amount, expiry_year, expiry_month, cvv, pin, suggested_auth, charge_type):

        if is_test:
            publickey = config('RAVE_PUBLIC_KEY_TEST')
            secretkey = config('RAVE_SECRET_KEY_TEST')
            production = False
        else:
            publickey = config('RAVE_PUBLIC_KEY')
            secretkey = config('RAVE_SECRET_KEY')
            production = True

        rave = Rave(publicKey=publickey, secretKey=secretkey,
                    production=False, usingEnv=False)

        currency = config('currency')
        reference = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(16))

        ud = UserDetails.objects.get(uuid=uuid)
        payload = {
            "cardno": card_number,
            "cvv": cvv,
            "expirymonth": expiry_month,
            "expiryyear": expiry_year,
            "currency": currency,
            "country": "NG",
            "amount": amount,
            "email": ud.user.email,
            "firstname": ud.user.first_name,
            "txRef": reference,
        }
        
        try:
            card = rave.Card
            initiate_charge = card.charge(payload)

            if initiate_charge["suggestedAuth"]:
                arg = Misc.getTypeOfArgsRequired(
                    initiate_charge["suggestedAuth"])

                if arg == "pin":
                    Misc.updatePayload(
                        initiate_charge["suggestedAuth"], payload, pin=pin)
                if arg == "address":
                    Misc.updatePayload(res["suggestedAuth"], payload, address={
                                       "billingzip": "07205", "billingcity": "Hillside", "billingaddress": "470 Mundet PI", "billingstate": "NJ", "billingcountry": "US"})
                res = rave.Card.charge(payload)

            # if res["validationRequired"]:
            #     rave.Card.validate(res["flwRef"], "12345")

            # res = rave.Card.verify(res["txRef"])

            return res

        except RaveExceptions.CardChargeError as e:
            return{
                "error": True,
                "error_message": e.err["errMsg"],
                "ref": e.err["flwRef"]
            }

    @staticmethod
    def authorize(is_test, reference, otp):
        rave = test_check(is_test)
        get_transaction = Transaction.objects.get(reference=reference)
        if (get_transaction.status == "SUCCESS") or (get_transaction.status == "FAILED"):
            return{
                "error": True,
                "error_message": "can't authorize {0} transaction".format(get_transaction.status.lower()),
                "ref": reference
            }
        if (get_transaction.status == "PENDING VALIDATION") or (get_transaction.status == 'SPV'):
            try:
                authorize = rave.Card.validate(
                    get_transaction.payment_reference, otp)
            except RaveExceptions.TransactionValidationError as e:
                return{
                    "error": True,
                    "error_message": e.err['errMsg'],
                    "ref": e.err["flwRef"]
                }
        try:
            verify = rave.Card.verify(authorize['txRef'])
        except RaveExceptions.TransactionVerificationError as e:
            return {
                "error": True,
                "error_message": e.err["errMsg"],
                "ref": e.err["flwRef"]
            }
        return verify

    @staticmethod
    def transfer(is_test, account_number, account_bank, amount, currency, beneficary_name):
        rave = test_check(False)

        try:
            url = 'https://api.flutterwave.com/v3/transfers/'
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(config('RAVE_SECRET_KEY'))}
            res = requests.request("POST", url, headers=headers, data={
                "account_bank": account_bank,
                "account_number": account_number,
                "amount": amount,
                "narration": "New transfer",
                "currency": "NGN",
                "beneficiary_name": beneficary_name,
                "callback_url": "https://simplefi-develop.herokuapp.com/api/services/transfer-webhook",
            })

            return res
            print(res)
            balanceres = rave.Transfer.getBalance("NGN")
            print(balanceres)
        except RaveExceptions.IncompletePaymentDetailsError as e:
            print("incomplete")
            # return{
            #     "error": True,
            #     "error_message": e.err['errMsg'],
            #     "ref": e.err["flwRef"]
            # }
        except RaveExceptions.InitiateTransferError as e:
            print("initiate")
            # return{
            #     "error": True,
            #     "error_message": e.err['errMsg'],
            #     "ref": e.err["flwRef"]
            # }
        except RaveExceptions.TransferFetchError as e:
            print("transfer")
            # return{
            #     "error": True,
            #     "error_message": e.err['errMsg'],
            #     "ref": e.err["flwRef"]
            # }

        except RaveExceptions.ServerError as e:
            print("server")
            # return{
            #     "error": True,
            #     "error_message": e.err['errMsg'],
            #     "ref": e.err["flwRef"]
            # }

    @staticmethod
    def verify_transfer(is_test, id):
        rave = test_check(is_test)

        url = 'https://api.flutterwave.com/v3/transfers/{}'.format(id)

        if is_test:
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(config('RAVE_SECRET_KEY_TEST'))}
        else:
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(config('RAVE_SECRET_KEY'))}

        try:
            response = requests.request(
                "GET", url, headers=headers)

            return response.json()
        except RaveExceptions.TransferFetchError as e:
            return{
                "error": True,
                "error_message": e.err['errMsg'],
                "ref": e.err["flwRef"]
            }

    @staticmethod
    def airtime(is_test, amount, phone, reference):
        rave = test_check(is_test)

        url = 'https://api.flutterwave.com/v3/bills'

        if is_test:
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(config('RAVE_SECRET_KEY_TEST'))}
        else:
            headers = {"Content-Type": "application/json",
                       "Authorization": "Bearer {}".format(config('RAVE_SECRET_KEY'))}

        payload = {
            "country": "NG",
            "customer": '+234{}'.format(phone), "amount": str(amount),
            "recurrence": "ONCE",
            "type": "AIRTIME",
            "reference": reference
        }

        try:
            response = requests.request(
                "POST", url, headers=headers, data=payload)

            return response.json()
        except RaveExceptions.IncompletePaymentDetailsError as e:
            return{
                "error": True,
                "error_message": e.err['errMsg'],
                "ref": e.err["flwRef"]
            }


{
    'validationRequired': True,
    'suggestedAuth': u'PIN',
    'flwRef': None,
    'authUrl': None,
    'error': False,
    'txRef': 'MC-1538095398058'
}
