from datetime import datetime
import json
from decouple import config
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
import datetime
def defaultconverter(o):
  if isinstance(o, datetime.timedelta):
      return o.__str__()
  
def refreshToken():
        access = requests.post(config('ZOHO_REFRESH_TOKEN_URL'))
        response = json.loads(access.text)
        access_token = response["access_token"]
        return access_token

class LoanSign:

    
    @staticmethod
    def send_signature(firstname, lastname, email, date, payment_duration, interest_due, amount, repayment_amount):
        access_token = refreshToken()
        url = f"{config('ZOHO_URL')}/api/v1/templates/232975000000011093/createdocument"
        data = {
            "templates": {
                "field_data": {
                    "field_text_data": {"Full name": firstname+ " "+ lastname, "Email": email, "Date - 1": date.strftime("%Y-%M-%d"), "Text - 1": amount,
                                        "Text - 2": " {}".format(payment_duration), "Text - 4": f" {repayment_amount}" },
                    "field_boolean_data": {},
                    "field_date_data": {}
                },
                "actions": [
                    {
                        "recipient_name": firstname + " "+ lastname,
                        "recipient_email": email,
                        "action_id": "232975000000011106",
                        "signing_order": 1,
                        "role": "Owner",
                        "verify_recipient": False,
                        "private_notes": ""
                    }
                ],
                "notes": ""
            }
        }
        headers = {
            "Authorization": "Zoho-oauthtoken {}".format(access_token)
        }
        send_document = requests.post(
            url,
            data=json.dumps(data, default = defaultconverter),
            headers=headers
        )
        response = json.loads(send_document.text)
        return response


class InvestSign:

    @staticmethod
    def send_signature(firstname, lastname, email, date, payment_duration, interest_due, amount, repayment_amount):

        access_token = refreshToken()
        url = f"{config('ZOHO_URL')}/api/v1/templates/232975000000011131/createdocument"
        data = {
            "templates": {
                "field_data": {
                    "field_text_data": {"amount": amount},
                    "field_boolean_data": {},
                    "field_date_data": {}
                },
                "actions": [
                    {
                        "recipient_name": firstname + " "+ lastname,
                        "recipient_email": email,
                        "action_id": "232975000000011144",
                        "signing_order": 1,
                        "role": "Owner",
                        "verify_recipient": False,
                        "private_notes": ""
                    }
                ],
                "notes": ""
            }
        }
        headers = {
            "Authorization": "Zoho-oauthtoken {}".format(access_token)
        }
        send_document = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        response = json.loads(send_document.text)
        return response

@api_view(['POST'])
def test_sign(request):
        access_token = refreshToken()
        url = f"{config('ZOHO_URL')}/api/v1/templates/232975000000011093/createdocument"
        data = {
            "templates": {
                "field_data": {
                    "field_text_data": {"Full name": "firstname"+ " "+ "lastname", "Email": "email", "Date - 1": "date", "Text - 1": "amount",
                                        "Text - 2": "payment_duration", "Text - 4": "repayment_amount" },
                    "field_boolean_data": {},
                    "field_date_data": {}
                },
                "actions": [
                    {
                        "recipient_name": "firstname" + " "+ "lastname",
                        "recipient_email": "sylvia.onwukwe@gmail.com",
                        "action_id": "232975000000011106",
                        "signing_order": 1,
                        "role": "Owner",
                        "verify_recipient": False,
                        "private_notes": ""
                    }
                ],
                "notes": ""
            }
        }
        headers = {
            "Authorization": "Zoho-oauthtoken {}".format(access_token)
        }
        send_document = requests.post(
            url,
            data=json.dumps(data),
            headers=headers
        )
        response = json.loads(send_document.text)
        return Response({"message": response})