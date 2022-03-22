import json
import hashlib
import base64
import requests
from decouple import config
from transaction.utils import generate_transaction_reference
import datetime


def setup_mandate(ud: object , amount: int):
    
    request_id = generate_transaction_reference()
    body = config('REMITA_TEST_MERCHANT_ID') + config('REMITA_TEST_SERVICE_TYPE_ID') + request_id + str(amount)
    date = datetime.date.today()
    end_date = (date + datetime.timedelta(days=80)).strftime("%d/%m/%Y")
    
    start_date = date.strftime("%d/%m/%Y")
    
    post_data = {
        "merchantId":config('REMITA_TEST_MERCHANT_ID'),
        "serviceTypeId":config('REMITA_TEST_SERVICE_TYPE_ID'),
        "hash": '{}'.format(base64.b64encode(hashlib.sha512(body.encode()).digest())),
        "payerName":ud.user.first_name + " " + ud.user.last_name,
        "payerEmail":ud.user.email,
        "payerPhone":ud.phone,
        "payerBankCode":"057",
        "payerAccount":"0035509366",
        "requestId":request_id,
        "amount":amount,
        "startDate":start_date,
        "endDate":end_date,
        "mandateType":"DD",
        "maxNoOfDebits": "10"
    }
    
    print(post_data)
    url = config('REMITA_TEST_BASE_URL')+'exapp/api/v1/send/api/echannelsvc/echannel/mandate/setup'
    headers = {'Content-type':'application/json'}
    request_data = json.dumps(post_data)
    
    request = requests.post(url=url, headers=headers, data=request_data)
    print(request)
    response = json.loads(request.text)
    return response

def mandate_activate_request_otp(requestId, mandateId):
    
    reference = generate_transaction_reference()
    today = datetime.datetime.now()
    timeStamp = "{}-{}-{}T{}:{}:{}+000000".format(today.year, today.month, today.day, today.hour, today.second)
    body = config('REMITA_TEST_API_KEY') + reference + config('REMITA_TEST_API_TOKEN')
    
    url = config('REMITA_TEST_BASE_URL')+'exapp/api/v1/send/api/echannelsvc/echannel/mandate/setup'
    headers = {
        'Content-type':'application/json',
        'MERCHANT_ID':config('REMITA_TEST_MERCHANT_ID'),
        'API_KEY':config('REMITA_TEST_API_KEY'),
        'REQUEST_ID':reference,
        'REQUEST_TS':timeStamp,
        'API_DETAILS_HASH':'{}'.format(base64.b64encode(hashlib.sha512(body.encode()).digest()))
    }
    
    post_data = {
        "requestId": requestId,
        "mandateId": mandateId,
    }
    
    request_data = json.dumps(post_data)
    
    request = requests.post(url=url, headers=headers, data=request_data)
    print(request)
    response = json.loads(request.text)
    return response



def mandate_activate_request_otp(requestId, mandateId):
    
    reference = generate_transaction_reference()
    today = datetime.datetime.now()
    timeStamp = "{}-{}-{}T{}:{}:{}+000000".format(today.year, today.month, today.day, today.hour, today.second)
    body = config('REMITA_TEST_API_KEY') + reference + config('REMITA_TEST_API_TOKEN')
    
    url = config('REMITA_TEST_BASE_URL')+'exapp/api/v1/send/api/echannelsvc/echannel/mandate/setup'
    headers = {
        'Content-type':'application/json',
        'MERCHANT_ID':config('REMITA_TEST_MERCHANT_ID'),
        'API_KEY':config('REMITA_TEST_API_KEY'),
        'REQUEST_ID':reference,
        'REQUEST_TS':timeStamp,
        'API_DETAILS_HASH':base64.b64encode(hashlib.sha512(body.encode()).digest())
    }
    
    post_data = {
        "requestId": requestId,
        "mandateId": mandateId,
    }
    
    request_data = json.dumps(post_data)
    
    request = requests.post(url=url, headers=headers, data=request_data)
    response = json.loads(request.text)
    print(response)
    return response

def mandate_validate_request_otp(remitaTransRef, otp, card):
    
    reference = generate_transaction_reference()
    today = datetime.datetime.now()
    timeStamp = "{}-{}-{}T{}:{}:{}+000000".format(today.year, today.month, today.day, today.hour, today.second)
    body = config('REMITA_TEST_API_KEY') + reference + config('REMITA_TEST_API_TOKEN')
    
    url = config('REMITA_TEST_BASE_URL')+'exapp/api/v1/send/api/echannelsvc/echannel/mandate/setup'
    headers = {
        'Content-type':'application/json',
        'MERCHANT_ID':config('REMITA_TEST_MERCHANT_ID'),
        'API_KEY':config('REMITA_TEST_API_KEY'),
        'REQUEST_ID':reference,
        'REQUEST_TS':timeStamp,
        'API_DETAILS_HASH':'{}'.format(base64.b64encode(hashlib.sha512(body.encode()).digest()))
    }
    
    post_data = {
        "remitaTransRef": remitaTransRef,   
        "authParams": [
            {          
                "param1": "OTP",
                "value": otp
            },
            {          
                "param2": "CARD",
                "value": card
            }
        ]
    }
    
    request_data = json.dumps(post_data)
    
    request = requests.post(url=url, headers=headers, data=request_data)
    response = json.loads(request.text)
    print(response)
    return response


def mandate_status(mandateId, requestId):

    
    url = config('REMITA_TEST_BASE_URL')+'exapp/api/v1/send/api/echannelsvc/echannel/mandate/status'
    headers = {
        'Content-type':'application/json',
    }
    
    body = mandateId + config('REMITA_TEST_MERCHANT_ID')  + requestId + config('REMITA_TEST_API_KEY')

    post_data = {
        "merchantId": config('REMITA_TEST_MERCHANT_ID'),
        "mandateId": mandateId,
        "hash": hashlib.sha512(body.encode()).digest(),
        "requestId": requestId
    }
    
    request_data = json.dumps(post_data)
    
    request = requests.post(url=url, headers=headers, data=request_data)
    response = json.loads(request.text)
    print(response)
    return response



    
    