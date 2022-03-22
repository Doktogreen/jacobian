from datetime import datetime
from .models import UserDetails, Verifyme
from django.contrib.auth.models import User
import requests
import json
from decouple import config
from rest_framework.response import Response
from datetime import datetime


# def get_crm_token():
#     query = "{}middleware/oauth/token".format(config("CRM_PROD_URL"))
#     data = {
#         "userName": "SimpleFI",
#         "password": "test@Password"
#     }
#     data = json.dumps(data)
#     response = requests.post(query, data=data, headers={
#         "Content-Type": "application/json"})
#     response = json.loads(response.text)
#     return response



class Verification:

    @staticmethod
    def youverify_setup(idnum, idtype, lastname, firstname, dob):
        url = config("YOUVERIFY_URL")+"identities/candidates/check"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({ 
            "report_type": "identity", 
            "type": idtype, 
            "reference": idnum,
            "last_name": lastname,
            "first_name": firstname,
            "subject_consent": True
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        return response.text
    
    @staticmethod
    def youverify_business(business_name):
        url = config("YOUVERIFY_URL")+"backgrounds/cac"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({
            "company_name": business_name
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        return response.text
    
    @staticmethod
    def youverify_bvn(bvn, first_name, last_name):
        url = config("YOUVERIFY_URL")+"identities/candidates/check"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({ 
            "report_type": "identity",
            "type": "ibvn",
            "reference": bvn,
            'first_name': first_name,
            'last_name': last_name,
            "subject_consent": True
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        return json.loads(response.content)

    def youverify_candidate(firstname, lastname, email, phone):
        url = config("YOUVERIFY_URL")+"candidates/"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({ 
            "first_name": firstname,
            "last_name": lastname,
            "email": email, 
            "mobile": phone, 
            "country": "Nigeria"
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        response = json.loads(response.text)
        return response['data']['id']
        

    @staticmethod
    def addressVerification(candidate_id, street, state, lga, photo):
        url = config("YOUVERIFY_URL")+"candidates/"+candidate_id+"/live_photo"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({
            "address":
            {
            "building_number": "1",
            "street": street,
            "landmark": street,
            "state": state,
            "city": lga,
            "country": "Nigeria",
            },
            "images": [photo]
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        response = json.loads(response.text)
        return response['status_code']

    def businessAddressVerification(candidate_id, business_name,rc_number, email, phone, street, state, lga):
        url = config("YOUVERIFY_URL")+"candidates/"+candidate_id+"/merchants"
        token = config("YOUVERIFY_TOKEN")
        headers = {
            "Content-Type": "application/json",
            "token": token
        }
        data = json.dumps({ 
        "merchant": {
            "name": business_name,
            "registration_number": rc_number,
            "email": email,
            "mobile": phone
        },
            "address": 
            {
            "building_number": "1", 
            "street": street,
            "landmark": street,
            "state": state,
            "city": lga,
            "country": "Nigeria",
            }
        })
        response = requests.post(
            url,
            data = data,
            headers = headers
        )
        response = json.loads(response.text)
        return response['status_code']

class CRM:
    @staticmethod
    def create_crm(request, bvn, email, birthdate, first_name, middle_name, last_name, phone, address):
        date_of_birth = datetime.strptime(
            str(birthdate), "%Y-%m-%d").strftime("%d %b %Y")
        data = {           
            "firstName" : first_name,
            "lastName" : last_name,
            "middleName" : "",
            "externalId" : bvn,
            "savingsProductId" : 1,
            "emailAddress" : email,
            "mobileNo" : phone,
            "bvn" : bvn,
            "professionId" : 1,
            "street" : address,
            "dateOfBirth" : date_of_birth,
            "genderId" : 51
        }
        request_data = json.dumps(data)
        if request.method == 'POST':
            # get_token = get_crm_token()
            query = "{}integration-service/api/v1/customers/".format(config("CRM_PROD_URL"))
            response = requests.post(
                query,
                data=request_data,
                verify=False,
                headers={
                    "Content-Type": "application/json",
                    "API-KEY": "s68WOu6QCAKmPHxAK3TJeg=="
                }
            )
            response = json.loads(response.text)
            print(response)
            return response

    @staticmethod
    def create_crm_coporate(name, external_id, bvn, email, phone, address,
        savings_product_id = 1, 
        client_classfication_id = 25, 
        client_non_person_constituition = 57,
        client_non_person_main_business_line = 14):
        data = {
            "name": name,
            "externalId": external_id,
            "savingsProductId": savings_product_id,
            "emailAddress": email,
            "mobileNo": phone,
            "bvn": bvn,
            "clientClassificationId": client_classfication_id,
            "street": address,
            "clientTypeId": 50,
            "clientNonPersonDetails": {
                "mainBusinessLineId": client_non_person_main_business_line,
                "constitutionId": client_non_person_constituition
            }
        }

        data = json.dumps(data)
        CRM_URL = config("CRM_URL")
        url = f"{CRM_URL}integration-service/api/v1/customers?customer-type=CORPORATE"
        response = requests.post(
            url,
            data,
            verify=False,
            headers={
                "Content-Type": "application/json",
                "API-KEY": config("CRM_API_KEY")
            }
        )
        response = json.loads(response.text)
        print(response)
        return response