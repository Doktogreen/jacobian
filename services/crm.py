from datetime import date, datetime
import json
import requests
from django.shortcuts import get_object_or_404
from users.models import UserDetails, Business
from users.verification import CRM
from loan.sign import LoanSign
from loan.models import Loan, Repayment
from decouple import config
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from sendgrid.helpers.mail import Mail
from sendgrid import SendGridAPIClient
from .serializers import CoporateCustomerSerializer

# search user
def get_client_id(bvn, phone_number):
    print(bvn)
    url = config("CRM_PROD_URL")+'''fineract-provider/api/v1/search?exactMatch=false
    &query={}&resource=clients,clientIdentifiers'''.format(bvn)
    response = requests.get(
    url,
    verify = False,
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {config('CRM_BASIC_KEY')}",
        "Fineract-Platform-TenantId": "default"
        }
    )
    if len(json.loads(response.content)) == 0:
        
        print(phone_number)
        url = config("CRM_PROD_URL")+'''fineract-provider/api/v1/search?exactMatch=false
        &query={}&resource=clients,clientIdentifiers'''.format(phone_number)
        response = requests.get(
        url,
        verify = False,
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {config('CRM_BASIC_KEY')}",
            "Fineract-Platform-TenantId": "default"
            }
        )
        if len(json.loads(response.content)) == 0:
            return None
        else:
            print(json.loads(response.content)[0]['entityId'])
            return json.loads(response.content)[0]['entityId']
    else:
        
        print(json.loads(response.content)[0]['entityId'])
        return json.loads(response.content)[0]['entityId']

@ api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_customer(request):
    ud = get_object_or_404(UserDetails, user=request.user)
    if ud.account_type == "Individual":
        bvn=ud.individual.identification_number
        phone = ud.phone
        dob = ud.individual.dob
        address = ud.individual.address
    else:
        bvn= ud.business.shareholder1_identification_number
        phone = ud.phone
        dob = date.today()
        address = ud.business.office_address
    client_details = get_client_id(bvn, phone)
    if client_details == None:
        register_in_crm = CRM.create_crm(request=request,
                bvn=bvn, email=ud.user.email,
                birthdate=dob,
                first_name=ud.user.first_name,
                middle_name=ud.user.last_name,
                last_name=ud.user.last_name,
                phone=phone,
                address=address)
        if 'globalisationMessageCode' in register_in_crm:
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
                message = Mail(
                        from_email="support@simplefinance.ng",
                        to_emails=["support@simplefinance.ng", "admin@simplefing.com"],
                        subject='Loan Creation Failed',
                        html_content='''
                        Hello Admin,
                        A customer just tried to apply for a loan. The request was unsuccessful because user already
                        has an existing email address not associated with his/her bvn and phone number. Kindly update user's account
                        to continue
                        <p>Customer Fullname: {0} {1} </p>
                        <p>Customer Email: {2} </p>
                        <p>Customer Phone Number: {3} </p>
                                    '''.format( ud.user.first_name, ud.user.last_name, ud.user.email, ud.phone)
                        )

                sg = SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
                sg.send(message)
                return Response({
                        "message": "Your request could not be completed because you have an existing record on our system, please contact admin to update your record",
                        "error": register_in_crm['globalisationMessageCode']
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({
                        "message": "Your request failed, Kindly complete KYC on profile page and try again",
                        "error": register_in_crm['globalisationMessageCode']
                    }, status=status.HTTP_400_BAD_REQUEST)
        else:
            clientId = register_in_crm['clientId']
            return Response({
                    "message": "User Created Successfully",
                    "data": clientId
                }, status=status.HTTP_200_OK)
    else:
        return Response({
            "message": "User Identified",
            "data": client_details
        })

@ api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_coporate_customer(request):
    ud = get_object_or_404(UserDetails, user=request.user, account_type="Business")
    business = get_object_or_404(Business, user=ud)
    data = CoporateCustomerSerializer(data=request.data)
    if data.is_valid():
        crm_data = {
            "name": business.company_name,
            "external_id": business.rc_number,
            "savings_product_id": data.validated_data.get("savings_product"),
            "email": business.email,
            "phone": business.phone,
            "bvn": ud.bvn,
            "client_classification_id": data.validated_data.get("client_classification"),
            "address": business.office_address,
            "client_non_person_constituition": data.validated_data.get("client_non_person_constituition"),
            "client_non_person_main_business_line": data.validated_data.get("client_non_person_main_business_line")
        }

        client_details = get_client_id(crm_data["bvn"], crm_data["phone"])
        if client_details == None:
            register_in_crm = CRM.create_crm_coporate(**crm_data)
            if 'globalisationMessageCode' in register_in_crm:
                if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
                    message = Mail(
                            from_email="support@simplefinance.ng",
                            to_emails=["support@simplefinance.ng", "admin@simplefing.com"],
                            subject='Loan Creation Failed',
                            html_content='''
                            Hello Admin,
                            A customer just tried to apply for a loan. The request was unsuccessful because user already
                            has an existing email address not associated with his/her bvn and phone number. Kindly update user's account
                            to continue
                            <p>Customer Fullname: {0} {1} </p>
                            <p>Customer Email: {2} </p>
                            <p>Customer Phone Number: {3} </p>
                                        '''.format( ud.user.first_name, ud.user.last_name, ud.user.email, ud.phone)
                            )

                    sg = SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
                    sg.send(message)
                    return Response({
                            "message": "Your request could not be completed because you have an existing record on our system, please contact admin to update your record",
                            "error": register_in_crm['globalisationMessageCode']
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({
                            "message": "Your request failed, Kindly complete KYC on profile page and try again",
                            "error": register_in_crm['globalisationMessageCode']
                        }, status=status.HTTP_400_BAD_REQUEST)
            else:
                clientId = register_in_crm['clientId']
                return Response({
                        "message": "User Created Successfully",
                        "data": clientId
                    }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "User Identified",
                "data": client_details
            })


def loanCRM(clientId, amount, payment_duration):
    baseurl = config("CRM_PROD_URL")+"integration-service/api/v1/loan-accounts/"
    print("{}".format(f'{amount:,}'))
    data = {
        # clientId: clientId,
        "clientId" : clientId,
        "productId" : 5,
        "principal" : "{}".format(f'{amount:,}'),
        "loanTermFrequency" : payment_duration,
        "loanTermFrequencyType" : 2,
        "loanType" : "individual",
        "numberOfRepayments" : payment_duration,
        "repaymentEvery" : 1,
        "repaymentFrequencyType" : 2,
        "interestRatePerPeriod" : 10.0,
        "amortizationType" : 1,
        "interestType" : 0,
        "interestCalculationPeriodType" : 1,
        "transactionProcessingStrategyId" : 1
    }
    request_data = json.dumps(data)
    response = requests.post(
        baseurl,
        data=request_data,
        verify = False,
        headers = {
            "Content-Type": "application/json",
            "API-KEY": config('CRM_API_KEY')
        }
    )
    response = response
    return response
# create a loan
@ api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_loan(request):
    '''
    THIS IS AN ENDPOOINT TO CREATE LOAN ON THE CRM
    '''
    body = json.loads(request.body)
    clientId= body['clientId']
    amount= body['amount']
    payment_duration= body['payment_duration']
    ud = get_object_or_404(UserDetails, uuid=body['uuid'])
    
    create_loan = loanCRM(clientId, amount, payment_duration)
    loan_detail = get_loan_account_detail(json.loads(create_loan.content)['loanId'])
    print(json.loads(create_loan.content)['loanId'])
    if create_loan.status_code != 202:
        return Response({
            "message": "Loan Creation Failed, Please Try Again or Contact Admin",
            "error": json.loads(create_loan.text)
        }, status=status.HTTP_400_BAD_REQUEST)
    client=ud
    mature_date = date(loan_detail['timeline']['expectedMaturityDate'][0], loan_detail['timeline']['expectedMaturityDate'][1], loan_detail['timeline']['expectedMaturityDate'][2])
    loan = Loan.objects.create(user=ud,
                               crm_loan_id = loan_detail['id'],
                               amount=loan_detail['principal'],
                               total_repayment= loan_detail['repaymentSchedule']['totalRepaymentExpected'],
                               repayment_amount = loan_detail['repaymentSchedule']['totalRepaymentExpected'],
                               amount_paid = 0.0,
                               payment_duration=loan_detail['termFrequency'],
                               interest = loan_detail['repaymentSchedule']['totalInterestCharged'],
                               status = "Pending",
                               maturity_date = mature_date)
    loan.save()
    # create repayment plan
    for i in range(1, loan_detail['termFrequency'] + 1):
        payment_date = date(loan_detail['repaymentSchedule']['periods'][i]['dueDate'][0], loan_detail['repaymentSchedule']['periods'][i]['dueDate'][1], loan_detail['repaymentSchedule']['periods'][i]['dueDate'][2])
        Repayment.objects.create(user=ud, loan=loan, total_amount=loan_detail['repaymentSchedule']['periods'][i]['principalOriginalDue'], paid=False,
                                     amount_paid=0.0, outstanding=loan_detail['repaymentSchedule']['periods'][i]['principalLoanBalanceOutstanding'],
                                     amount_due=loan_detail['repaymentSchedule']['periods'][i]['principalOriginalDue'], payment_date=payment_date)
    message = Mail(
            from_email="support@simplefinance.ng",
            to_emails=["support@simplefinance.ng", "admin@simplefing.com"],
            subject='Loan Application',
            html_content='''
            Hello Admin,
            A customer just applied for a loan, kindly log on and review.
            <p>Customer Fullname: {0} {1} </p>
            <p>Customer Email: {2} </p>
            <p>Customer Phone Number: {3} </p>
                        '''.format( client.user.first_name, client.user.last_name, client.user.email, client.phone)
                        )

    print(config('SENDGRID_API_KEY'))
    # sg = SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
    # sg.send(message)
    
    sign = LoanSign.send_signature(firstname=client.user.first_name,
                                    lastname=client.user.last_name,
                                    email=client.user.email,
                                    date=datetime.now(),
                                    amount=body['amount'],
                                    payment_duration=str(loan_detail['termFrequency'])+" "+loan_detail['termPeriodFrequencyType']['value'],
                                    interest_due=loan_detail['repaymentSchedule']['totalInterestCharged'], repayment_amount=loan_detail['repaymentSchedule']['totalRepaymentExpected'])
        
    if sign['code'] == 0:
        pass
    else:
        message = Mail(
            from_email="support@simplefinance.ng",
            to_emails=["support@simplefinance.ng", "admin@simplefing.com"],
            subject='Loan Contract Not Sent',
            html_content='''
            Hello Admin,
            A customer just applied for a loan, but unable to recieve the loan contract for the following reason:
            <p>Error: {4}</p>
            <p>Customer Fullname: {0} {1} </p>
            <p>Customer Email: {2} </p>
            <p>Customer Phone Number: {3} </p>
                        '''.format( client.user.first_name, client.user.last_name, client.user.email, client.phone, sign['message'])
            )

    # sg = SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
    # sg.send(message)
    return Response({
        "message": "Loan Created Successfully",
    }, status=status.HTTP_201_CREATED)

@ api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_repayment(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    if ud.account_type == "Individual":
        bvn=ud.individual.identification_number
    else:
        bvn= ud.business.shareholder1_identification_number
    # get loan accounts
    url = config('CRM_PROD_URL')+"fineract-provider/api/v1/clients/{}/accounts".format(get_client_id(bvn, ud.phone))
    print(url)
    response = requests.get(
    url,
    verify = False,
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {config('CRM_BASIC_KEY')}",
        "Fineract-Platform-TenantId": "default"
        }
    )
    accountIds = []
    repayment = []
    print(json.loads(response.content))
    for i in range(0, len(json.loads(response.content)['loanAccounts']) ):
        accountId = json.loads(response.content)['loanAccounts'][i]['id']
        accountIds.append(accountId)
    for id in accountIds:
        baseurl = config("CRM_PROD_URL")+"integration-service/api/v1/loan-accounts/"+str(id)+"/repayment-schedule"
        response = requests.get(
            baseurl,
            verify = False,
            headers = {
                "Content-Type": "application/json",
                "API-KEY": config('CRM_API_KEY')
            }
        )
        response = json.loads(response.content)
        plan = {}
        plan['details'] = {}
        plan['details']['totalPrincipalDisbursed'] = response['repaymentSchedule']['totalPrincipalDisbursed']
        plan['details']['totalPrincipalPaid'] = response['repaymentSchedule']['totalPrincipalPaid']
        plan['details']['totalRepayment'] = response['repaymentSchedule']['totalRepayment']
        plan['details']['totalRepaymentExpected'] = response['repaymentSchedule']['totalRepaymentExpected']
        plan['periods'] = response['repaymentSchedule']['periods']
        plan['active'] = response['status']['active']
        plan['pending'] = response['status']['pendingApproval']
        plan['loanId'] = response['id']
        repayment.append(plan)
    return Response({
        "message": "Successful",
        "data": repayment
    }, status=status.HTTP_200_OK)
    
def get_loan_account_detail(id):
    baseurl = config("CRM_PROD_URL")+"integration-service/api/v1/loan-accounts/"+str(id)+"/repayment-schedule"
    response = requests.get(
        baseurl,
        verify = False,
        headers = {
                "Content-Type": "application/json",
                "API-KEY": config('CRM_API_KEY')
        }
    )
    response = json.loads(response.content)
    return response
        

@ api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def repay_loan(request):
    body = json.loads(request.body)
    client = get_object_or_404(UserDetails, uuid=body['uuid'])
    loanId = body['loanId']
    amount= body['amount']
    transactionRef= body['transactionRef']
    baseurl = config("CRM_PROD_URL")+"integration-service/api/v1/loan-accounts/transactions"
    data = {
        "loanId" : loanId,
        "amount" : amount,
        "transactionRef" : transactionRef,
    }
    request_data = json.dumps(data)
    response = requests.post(
        baseurl,
        data=request_data,
        verify = False,
        headers = {
            "Content-Type": "application/json",
            "API-KEY": config('CRM_API_KEY')
        }
    )
    if response.status_code == 400:
        message = Mail(
            from_email="support@simplefinance.ng",
            to_emails=["support@simplefinance.ng", "admin@simplefing.com"],
            subject='Loan Paid But Not Updated on CRM',
            html_content='''
            Hello Admin,
            A customer just paid for a loan, but unable to update payment for the following reason:
            <p>Error: {4}</p>
            <p>Customer Fullname: {0} {1} </p>
            <p>Customer Email: {2} </p>
            <p>Customer Phone Number: {3} </p>
            <p>LoanId: {5}</p>
                        '''.format( client.user.first_name, client.user.last_name, client.user.email, client.phone, json.loads(response.text)["globalisationMessageCode"], loanId)
            )

    sg = SendGridAPIClient(api_key=config('SENDGRID_API_KEY'))
    sg.send(message)
    response = json.loads(response.text)
    # print(response.status_code)
    return Response({
        "status": "Successful",
        "data": response
    }, status=status.HTTP_200_OK)