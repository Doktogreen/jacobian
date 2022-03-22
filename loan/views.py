from email import message
import requests
from django.http import JsonResponse
import json
import http.client
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from users import views
from users.serializers import EmployeeSerializer, NextofKinSerializer
from .models import Loan, Repayment, Contract, Prediction
from .sign import LoanSign
from wallet.models import WitMono
from users.models import Profile, UserDetails
from wallet.models import Wallet
from services.models import Investment
from transaction.models import Transaction
from transaction.utils import generate_transaction_reference
from transaction.transaction_complete_hook import TransactionCompleteHook
from users.models import UserDetails, Individual, Employee, NextOfKin
from .serializers import LoanSerializer, RepaymentSerializer, ContractSerializer, CreateLoanSerializer, LoanKYCSerializer
from rest_framework.exceptions import APIException
from rest_framework.decorators import api_view, action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework import status, permissions
from django.forms.models import model_to_dict
from dateutil.relativedelta import relativedelta
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from middleware.response import *

# Create your views here.


class LoansViewSet(viewsets.ModelViewSet):
    queryset = UserDetails.objects.all()
    lookup_field = 'uuid'
    serializer_class = LoanSerializer

    """
    Loan ViewSet for this loan
    """

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance = Loan.objects.filter(user=instance)
        serializer = CreateLoanSerializer(instance, many=True)
        return success_response(data=serializer.data, message='User loans')

    def create(self, request, *args, **kwargs):
        body = json.loads(request.body)
        ud = ud = UserDetails.objects.get(user=request.user)
        serializer = LoanSerializer(data=body)
        serializer.is_valid(raise_exception=True)
        body = serializer.data

        # check if load exist
        if Loan.objects.filter(user=ud).filter(status='Pending').exists():
            return error_response(message="Pending Loan Exists", status=200)
        if Loan.objects.filter(user=ud).filter(status='Approved').exists():
            return error_response(message="Please payoff your pending loan", status=200)

        amount = float(body["amount"])
        purpose = body["purpose"]
        payment_duration = body["payment_duration"]

        time = payment_duration / 12
        interest = amount * .045
        interest_due = interest * payment_duration
        total_repayment = amount + interest_due
        repayment_amount = total_repayment / payment_duration
        date = datetime.now()
        maturity_date = date + relativedelta(months=+payment_duration)

        # create loan record
        loan = Loan.objects.create(
            user=ud, amount=amount, purpose=purpose, payment_duration=payment_duration, interest=interest,
            admin_fee=2000.00, status="Pending", maturity_date=maturity_date, total_repayment=total_repayment,
            repayment_amount=repayment_amount, amount_paid=0.00, contract_status="Pending")

        # create esignature record
        sign = LoanSign.send_signature(
            firstname=ud.user.first_name, lastname=ud.user.last_name, email=ud.user.email, date=date, amount=amount,
            payment_duration=payment_duration, interest_due=interest_due, repayment_amount=repayment_amount)
        if sign['code'] == 0:
            if sign['requests']['request_status'] == 'inprogress':
                Contract.objects.create(
                    status="Sent",
                    name=ud.user.first_name + ' ' + ud.user.last_name,
                    email=ud.user.email,
                    mobile=ud.phone,
                    loan=loan
                )
        else:
            loan_id = model_to_dict(loan)['id']
            Loan.objects.filter(id=loan_id).update(status="denied")

        # create repayment plan
        for i in range(1, payment_duration + 1):
            payment_date = date + relativedelta(months=+i)
            Repayment.objects.create(user=ud, loan=loan, total_amount=amount, paid=False,
                                     amount_paid=repayment_amount, outstanding=total_repayment,
                                     amount_due=repayment_amount, payment_date=payment_date)
        return success_response(data=serializer.data, message="Loan created")


class RepaymentViews(viewsets.ReadOnlyModelViewSet):
    queryset = UserDetails.objects.all()
    serializer_class = RepaymentSerializer
    lookup_field = 'uuid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        loans = Loan.objects.filter(user=instance)
        loan = loans.filter(status="Approved")
        if len(loan) == 0:
            return Response({"data": "Your loan has not been approved, please check your email for your loan  agreement"})
        transaction = Repayment.objects.filter(loan=loan[0])
        print(transaction)
        queryset = self.filter_queryset(transaction)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = RepaymentSerializer(queryset, many=True)
        print(serializer.data)
        return Response({'status': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(['POST'])
def repayLoan(request):
    data = json.loads(request.body)
    ud = UserDetails.objects.get(uuid=data['uuid'])
    loan = Loan.objects.get(user=ud)
    wallet = Wallet.objects.get(user=ud)
    if float(data['amount']) > float(wallet.balance):
        return Response({"message": "Insufficient Wallet Balance"})
    else:
        newBalance = float(wallet.balance) - float(data['amount'])
        wallet.balance = newBalance
        wallet.save()
        transaction = Repayment.objects.get(id=data['id'])
        transaction.paid = True
        transaction.amount_paid = data['amount']
        transaction.save()

        newAmount = float(loan.amount_paid) + float(data['amount'])
        if newAmount != loan.total_repayment:
            loan.amount_paid = newAmount
            loan.save()
        else:
            loan.amount_paid = newAmount
            loan.status = "Completed"
            loan.save()
        Transaction.objects.create(
            amount=data['amount'],
            status='SUCCESS', transaction_type='loan-repayment', reference=generate_transaction_reference(),
            type='debit', user=ud, customer_email=ud.user.email, narration='Loan Repayment', currency='NGN')
        return Response({"message": "Payment successful"})


@csrf_exempt
@api_view(['POST'])
# @parser_classes([MultiPartParser, FormParser])
def loan_webhook(request):
    data = json.loads(request.body)
    email = data['requests']['actions'][0]['recipient_email']
    ud = User.objects.get(email=email)
    user = UserDetails.objects.get(user=ud)
    if data['requests']["document_ids"][0]['document_name'] == "Offer Letter.pdf":
        loan = Loan.objects.get(user=user)
        if data['requests']['request_status'] == "completed":
            # approve loan
            loan.status = 'Approved'
            loan.contract_status = 'Completed'
            loan.save()
            # increase user walletbalance
            ud.loan_amount = loan.amount
            newloan = user.wallet.balance + loan.amount
            user.wallet.balance = newloan
            user.save()
            transaction = Transaction.objects.create(
                amount=loan.amount, status='SPV', transaction_type='loan',
                reference=generate_transaction_reference(type='loan'),
                type='credit', user=user, customer_name=ud.first_name + ' ' + ud.last_name, customer_email=ud.email,
                narration='Loan Credit for' + ' ' + ud.first_name + ' ' + ud.last_name, currency='NGN')
            try:
                TransactionCompleteHook.credit(transaction_id=transaction.id)
                transaction.status = 'SUCCESS'
                transaction.save()
            except APIException:
                transaction.status = 'FAILED'
                transaction.narration = 'Loan Already Credited'
                transaction.save()
                return Response({'message': 'Loan Already credited'}, status=status.HTTP_200_OK)
            # notify user
            message = Mail(
                from_email="support@simplefinance.ng",
                to_emails=email,
                subject='Your Loan is Approved',
                html_content='''<p>Hello ''' + ud.first_name + "," +
                '''</p <p> Thanks for applying for a loan with us at Simplefinance.
             We’re your one-stop hub for getting collateral-free loans with the lowest interest rates and experiencing profitable investment opportunities. </p>
             <p>We just wanted to notify you that your loan has been approved, and your wallet has been credited.
             <p>Kindly ensure you complete your KYC and Identity verification, if not completed, to be able to withdraw funds from your digital wallet.</p>
             Download the SimpleFi App from the Play Store to keep track of your loan. <p>For more information, visit our website: www.simplefi.ng</p>
              <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to support@simplefinance.com </p>'''
            )
            try:
                sg = SendGridAPIClient('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')
                response = sg.send(message)
            except Exception as e:
                print(e)
            return Response("Loan Approved")
        else:
            # update loan
            loan.status = 'Denied'
            loan.contract_status = 'Denied'
            loan.save()
        serializer = LoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if data['requests']["document_ids"][0]['document_name'] == "Contract Letter.pdf":
        investment = Investment.objects.get(uuid=user)
        if data['requests']['request_status'] == "completed":
            investment.contract_status = "Approved"
            investment.status = "Approved"
            investment.save()
            return Response({"status": "successful", "message": "Investment Apprved"})
        else:
            investment.contract_status = "Denied"
            investment.status = "Denied"
            investment.save()
            return Response({"status": "successful", "message": "Investment Denied"})
    else:
        return Response({'message': 'invalid event-type'}, status=status.HTTP_200_OK)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    def list(self, req, pk=None):
        loan = Loan.objects.get(
            user=pk).distinct().order_by('-request_date')[0]
        userQueryset = Profile.objects.filter(
            user=pk).values_list('first_name', 'last_name')
        user = json.dumps(list(userQueryset), cls=DjangoJSONEncoder)
        emailQueryset = User.objects.filter(
            id=pk).values_list('email', flat=True)
        phoneQueryset = UserDetails.objects.filter(
            user=pk).values_list('phone', 'business_name')
        email = json.dumps(list(emailQueryset), cls=DjangoJSONEncoder)
        phone = json.dumps(list(phoneQueryset), cls=DjangoJSONEncoder)

        data = {
            "template_id": config('template_id'),
            "title": "Loan Agreement From Simplefing Limited",
            "metadata": "ID0001",
            "locale": "en",
            "test": "yes",
            "signers": [
                {
                    "name": json.loads(user)[0][0] + " " + json.loads(user)[0][1],
                    "email": json.loads(email)[0],
                    "mobile": json.loads(phone)[0][0],
                    "company_name": json.loads(phone)[0][1],
                    "redirect_url": "https://simplefi.ng",
                    "signing_order": "1",
                    "auto_sign": "no",
                    "embedded_sign_page": "no",
                    "embedded_redirect_iframe_only": "no",
                    "skip_signature_request": "no",
                    "skip_signer_identification": "no"
                }
            ],

            "emails": {
                "signature_request_subject": "Your loan contract is ready to sign",
                "signature_request_text": "Hi " + json.loads(user)[0][0] + " " + json.loads(user)[0][
                    1] + ", \n\n To review and sign the contract please press the button below \n\n Kind Regards",
                "final_contract_subject": "Your document is signed",
                "final_contract_text": "Hi " + json.loads(user)[0][0] + " " + json.loads(user)[0][
                    1] + ", \n\n Your document is signed.\n\nKind Regards",
                "cc_email_addresses": ["sylvia@simplefing.com"],
                "reply_to": "support@customdomain.com"
            },
            "custom_branding": {
                "company_name": "Simplefing Limited",
                "logo_url": "https://online-logo-store.com/yourclient-logo.png"
            }
        }
        headers = {'content-type': 'application/json'}
        contract = requests.post(
            config('SIGN_ENDPOINT') + "/api/contracts/", json=data, headers=headers)
        res = json.loads(contract.text)["data"]
        Contract.objects.create(status=res["contract"]["status"], contract_id=res["contract"]["id"],
                                template_name=res["contract"]["template_name"],
                                title=res["contract"]["title"], signers_id=res["contract"]["signers"][0]["id"],
                                name=res["contract"]["signers"][0]["name"],
                                email=res["contract"]["signers"][0]["email"],
                                mobile=res["contract"]["signers"][0]["mobile"],
                                company_name=res["contract"]["signers"][0]["company_name"], loan_id=loan
                                )
        # serializer = ContractSerializer(queryset, many=True)
        return Response("res['contract']['id']")


class LoanViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = Loan.objects.select_related("user")
    serializer_class = LoanSerializer

    @action(detail=True, methods=["post", "get"])
    def payments(self, request, pk=None):
        """
        get:
        Return a list of payments for a given loan.
        post:
        Create a new payment for a given loan.
        """
        obj = self.get_object()
        if request.method == "GET":
            print(obj)
            return Response(
                RepaymentSerializer(obj.repayment_set.all(), many=True).data,
                status=status.HTTP_200_OK,
            )


@api_view(['GET'])
def userLoans(request, pk):
    user = User.objects.get(id=pk)
    loans = Loan.objects.get(user=user)
    x = list(loans.values())
    return JsonResponse(x, safe=False)


class ContractsViewSet(viewsets.ModelViewSet):
    queryset = UserDetails
    serializer_class = ContractSerializer

# @ api_view(['POST', 'GET', 'PUT'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def create_loan_crm(request):
#     '''
#     THIS IS AN ENDPOOINT TO CREATE LOAN ON THE CRM FOR PARTNERS
#     '''
#     body = json.loads(request.body)
#     clientId= body['clientId']
#     amount= body['amount']
#     payment_duration= body['payment_duration']
#     create_loan = loanCRM(clientId, amount, payment_duration)
#     # create esignature record
#     client = Individual.objects.get(crm_clientId=body['clientId'])
#     sign = LoanSign.send_signature(firstname=client.user.user.first_name,
#                                     lastname=client.user.user.last_name,
#                                     email=client.user.user.email,
#                                     date=datetime.now(),
#                                     amount=body['amount'],
#                                     payment_duration="",
#                                     interest_due="", repayment_amount="")

#     return Response({
#         "message": "Loan Created Successfully",
#         "data": {
#                 "officeId": create_loan['officeId'],
#             "clientId": create_loan['clientId'],
#             "loanId": create_loan['loanId']
#         }
#     }, status=status.HTTP_201_CREATED)

# @csrf_exempt
# class TestBSWebhookViewSet(viewsets.ModelViewSet):
#     queryset = Contract.objects.all()
#     serializer_class = ContractSerializer

#     def create(self, req):
#         body = json.loads(req.body)
#         print(body)
#         return Response(body)


@api_view(['GET'])
def loan_prediction(request, uuid):
    user = UserDetails.objects.get(uuid=uuid)
    prediction = get_object_or_404(Prediction, user=user)
    try:
        x = prediction.amount
    except ObjectDoesNotExist:
        return JsonResponse({"Message": "No Prediction yet"})
    return JsonResponse(x, safe=False)


@api_view(['POST'])
def predict_with_mono(request):
    # Generate Token To Be Used in Receiving Account Statement from witmono
    body = json.loads(request.body)
    print(body)
    try:
        uuid = body['uuid']
    except KeyError as e:
        return Response({"error": "Bad Request", "message": "{}".format(e)}, status=status.HTTP_400_BAD_REQUEST)
    user = get_object_or_404(UserDetails, uuid=uuid)
    witmono_obj = WitMono.objects.get(uuid=user)
    print(witmono_obj)
    token = witmono_obj.code
    print(token)
    # user = get_object_or_404(UserDetails, uuid=uuid)
    # print(code)
    # conn = http.client.HTTPSConnection("api.withmono.com")
    # body1 = {
    #     "code": code
    # }
    # json_body = json.dumps(body1)
    # headers = {
    #     'mono-sec-key': 'live_sk_HMEAtfO7Bxtrb6gOnubw',
    #     'Content-type': 'application/json'
    # }
    # conn.request("POST", "/account/auth", json_body, headers)
    # res = conn.getresponse()
    # data = res.read()
    # response = json.loads(data)
    # print(response)
    # try:
    #     token = response['id']
    #     print(token)
    # except KeyError:
    #     return Response(response)
    # Retrieve Account Statement of Six Months
    conn2 = http.client.HTTPSConnection(config('BASEURL_MONO'))
    body2 = {
        "period": "6"
    }
    json_body2 = json.dumps(body2)
    headers2 = {
        'mono-sec-key': config("MONO_LIVE_KEY"),
        'Content-Type': 'application/json'
    }
    path = "/accounts/{}/statement".format(token)
    # path2 =
    # print(path)
    conn2.request("GET", path, json_body2, headers2)
    res2 = conn2.getresponse()
    data2 = res2.read()
    response2 = json.loads(data2)
    try:
        x = []
        print(response2)
        for transaction in response2['data']:
            if transaction['type'] == "credit":
                x.append(float(transaction['amount']))

        sum_of_credit = sum(x)
        average_monthly = sum_of_credit / 6
        calculate_interest = 0.045 * average_monthly
        principal_amount = average_monthly - calculate_interest
        pred = Prediction.objects.create(user=user, amount=principal_amount)
        pred.save()
    except KeyError:
        return Response(response2)
    try:
        x = []
        # print(response2)
        for transaction in response2['data']:
            if transaction['type'] == "debit":
                x.append(float(transaction['amount']))

        sum_of_debit = sum(x)

    except KeyError:
        return Response({"Failed": "Failed"})

    return Response({"Principal Amount": principal_amount,
                     "Total Credit": sum_of_credit,
                     "Total Debit": sum_of_debit}
                    )


"""

    payment = request.data
    payment["loan"] = pk
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
"""


@api_view(["GET"])
def load_score(request, uuid):
    try:
        #import pdb; pdb.set_trace()
        user = UserDetails.objects.get(uuid=uuid)
        score = calc_loan_score(user)

        return Response({'message': score}, status.HTTP_200_OK)
    except:
        pass
    return Response("You are eligible")


@api_view(['POST', 'GET'])
def loanScore(request, uuid):
    userdetails = UserDetails.objects.get(uuid=uuid)
    score = 0
    if userdetails.individual.address:
        score += 5
    if userdetails.individual:
        score += 5
    if userdetails.individual.photo_link:
        score += 5
    if userdetails.individual.identification_number:
        score += 5
    if hasattr(userdetails.individual, 'guarantor'):
        if userdetails.individual.guarantor.bvn:
            score += 5
        score += 5
    if hasattr(userdetails.individual, 'nextofkin'):
        if userdetails.individual.nextofkin.bvn:
            score += 5
        score += 5
    if hasattr(userdetails.individual, 'employee'):
        if userdetails.individual.employee.company_name:
            score += 5
        if userdetails.individual.employee.emp_status == 'employed':
            score += 5
        score += 5
    if userdetails.individual.onboarded:
        score += 5
    setDate = datetime.date(1990, 1, 1)
    if userdetails.individual.dob == setDate:
        score += 5

    try:
        if WitMono.objects.get(user=user).exist():
            score += 5
    except:
        score += 0

    return Response({'status': 'success', 'score': score}, status=status.HTTP_200_OK)


class KYC(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ud = UserDetails.objects.get(user=request.user)
        individual = Individual.objects.get(user=ud)
        employee_serializer = EmployeeSerializer(individual.employee)
        next_of_kin_serializer = NextofKinSerializer(individual.nextofkin)

        data = {
            "employee": employee_serializer.data,
            "next of kin": next_of_kin_serializer.data
        }
        return success_response(message="Loan KYC details", data=data)

    def post(self, request):
        ud = UserDetails.objects.get(user=request.user)
        serializer = LoanKYCSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        # update next of kin
        individual = Individual.objects.get(user=ud)
        NextOfKin.objects.update_or_create(
            individual=individual, defaults={'phone': data['nok_phone'], 'name': data['nextofkin_name'],
                                             'email': data['nextofkin_email'], 'relationship': data['nextofkin_title'],
                                             'phone': data['nok_phone']
                                             }
        )

        # update employment
        Employee.objects.update_or_create(
            individual=individual,
            defaults={'company_name': data['companyName'],
                      'start_date': data['employeeStartDate'],
                      'net_income': data['NetMonthlyIncome'],
                      'email': data['companyemail'],
                      'address': data['employeraddress'],
                      'staff_id': data['staff_id'],
                      'obiligation': data['obligation']})

        return success_response(message='Loan KYC updated')
