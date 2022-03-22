import requests as http
import random
from . import monnify


def generate_reference(name):
    username = "".join(name.split(' ')).upper()
    random_username = "SIMPLEFI-RA-" + username + \
        '-' + str(random.randint(10, 1000))
    return random_username


class ReservedAccount:
    @staticmethod
    def get_reserved_account_details(is_test, name, customer_email, customer_name):
        if is_test:
            clientSecretKey = 'N9BUPJRKT9EDGAXLZHNWLABWTYRJLSTS'
            api_key = "MK_TEST_J7KULKYRH4"
            currency_code = 'NGN'
            contract_code = '9541832831'
        else:
            clientSecretKey = 'FWX8L8HVMPQWJCM5XG8GHBVZZYHGLBWU'
            api_key = "MK_PROD_YGLVDQ85T2"
            currency_code = 'NGN'
            contract_code = '461131453659'

        get_auth = monnify.Monnify(api_key, clientSecretKey, is_test)
        try:
            reference = generate_reference(name)
            reserved_account = get_auth.createReserveAccount(
                accountReference=reference, accountName=name, currencyCode=currency_code, contractCode=contract_code, customerEmail=customer_email, customerName=customer_name)
            return reserved_account
        except Exception:
            return 'Sorry an Error occurred'
