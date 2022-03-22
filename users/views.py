from datetime import datetime, date
import hashlib
from rest_framework.request import Request
from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .utils import upload_image
from .emails import send_welcome_email
from .models import (
    Guarantor, Individual, Business, UserDetails, NextOfKin,
    Employee, VerifyAddress, IndividualDocuments, ResetPasswordToken
)
from .serializers import *
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, authentication_classes, parser_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, parsers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from . import serializers
import random
import string
import uuid
from subprocess import *
from wallet.models import Wallet
from wallet.providus import create_reserved_account_number
from services.crm import get_client_id
from .verification import Verification, CRM
from middleware.response import *
from account.views import send_email
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class RegisterUser(APIView):

    def post(self, request: Request):
        input_data = serializers.RegisterSerializer(data=request.data)
        if input_data.is_valid():
            valid = input_data.validated_data

            user = User.objects.create_user(
                username=valid.get("email"),
                email=valid.get("email"),
                first_name=valid.get("firstname"),
                last_name=valid.get("lastname"),
                password=valid.get("password"),
            )

            # create user token for authentication
            token = Token.objects.create(user=user)

            # create user details
            user_details = UserDetails.objects.create(
                user=user,
                account_type=valid.get('account_type'),
                bvn=valid.get('bvn'),
                token=token
            )

            # create account
            account_type = valid.get('account_type')
            account = Individual.objects.create(user=user_details) if account_type == 'Individual'\
                else Business.objects.create(
                    user=user_details,
                    company_name=valid.get('business_name')
            )

            # create account and wallet
            #account_number = create_reserved_account_number(f'{user.last_name} {user.first_name}', valid.get('bvn'))
            wallet = Wallet.objects.create(
                user=user_details,
                status='ACTIVE'
            )

            data = {
                'user': serializers.UserSerializer(user).data,
                'user-details': serializers.UserDetailSerializer(user_details).data,
                'wallet-balance': wallet.balance,
                'account_type': account_type
            }

            if account_type == 'Individual':
                data['kyc-status'] = account.get_kyc_status()
                data['account'] = serializers.IndividualSerializer(account).data
            else:
                data['account'] = serializers.BusinessSerializer(account).data

            # send welcome email
            name = user.first_name if account_type == "Individual" else account.company_name
            send_welcome_email(user.email, name)

            return Response({
                'success': True,
                'data': data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'error': input_data.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(('POST',))
def support_email(request):
    body = json.loads(request.body)
    ud = get_object_or_404(UserDetails, uuid=body['uuid'])
    email = ud.user.email
    message = Mail(
        from_email="support@simplefinance.ng",
        to_emails="support@simplefinance.ng",
        subject='Tech Support Needed',
        html_content='''
            <p>Subject: {0} </p>
            <p>Message: {1} </p>
            <p>Email: {2} </p>
                        '''.format(body['subject'], body['message'], email)
    )
    try:
        sg = SendGridAPIClient(
            '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')
        response = sg.send(message)
        return Response({"message": "Ticket Sent Successfully"})
    except Exception as e:
        print(e)
        return Response({"message": "Error  occured"})


# @csrf_exempt
# def verify_user(token, id):
#     req_token = token
#     user_id = id

# used to confirm if username exists during registration
def check_username(username, email):
    if User.objects.filter(email=email):
        return False
    else:
        return True


def get_users(self):
    userDetail = User.objects.all().values(
        'id', 'last_login', 'is_superuser', 'email', 'first_name', 'last_name',
        'is_active', 'date_joined'
    )
    # user = users.union(userDetail)
    return HttpResponse(userDetail)


@csrf_exempt
@api_view(('POST',))
def reset_password(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body['email']
        user = get_object_or_404(User, email=email)
        ud = UserDetails.objects.get(user=user)
        if ud.reset_token:
            reset_token = ResetPasswordToken.objects.get(token=ud.reset_token.token)
            reset_token.token = ''.join(random.choices(string.ascii_letters+string.digits, k=6)).upper()
            reset_token.status = "active"
            reset_token.save()
            token = reset_token.token
        else:
            reset_token = ResetPasswordToken.objects.create(token=''.join(
                random.choices(string.ascii_letters+string.digits, k=6)).upper(), status='active')
            reset_token.save()
            token = reset_token.token
            ud.reset_token = reset_token
            ud.save()

        mail_subject = "Reset Password"
        mail_html_content = "<p>Hello " + user.first_name + "," + "</p><p> Forgot your password</p><p>We recieved a request to reset the password for your account.</P><p>To reset your password, click on the link below and input token <p>" + \
            token+"</p> https://app.simplefinance.ng/reset/"+str(ud.uuid)+"<p>For more information, visit our website: www.simplefi.ng</p> <p>We’re here to help </p>Got questions? We have the answers! <p>Send questions to admin@simplefing.com </p>"
        send_email(email=ud.user.email, subject=mail_subject, html_content=mail_html_content)
        return Response({"message": "Reset Password Mail Sent"}, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(('POST',))
def verify_reset_password(request):
    if request.method == "POST":
        body = json.loads(request.body)
        uuid = body['uuid']
        reset_token = body['reset_token']
        new_password = body['new_password']

        ud = UserDetails.objects.get(uuid=uuid)

        if ud.reset_token.status == "expired":
            return Response({"message": "reset_token has expired"}, status=status.HTTP_400_BAD_REQUEST)

        if ud.reset_token.token == reset_token:
            user = User.objects.get(id=ud.user.id)
            user.set_password(new_password)
            user.save()
            ResetPasswordToken.objects.filter(id=ud.reset_token.id).update(token=''.join(
                random.choices(string.ascii_letters+string.digits, k=6)).upper(), status='expired')
            return Response({"message": "Reset Password Successful"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid reset token supplied"}, status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@csrf_exempt
@api_view(('POST',))
def login_user(request):
    if request.method == "POST":
        body = json.loads(request.body)
        username = body['username']
        password = body["password"]
        # request_user = User.objects.filter(email=email).values_list("password", flat=True)
        user = authenticate(username=username, password=password)
        if user is not None:
            if not user.is_active:
                return Response({"message": "Account deactivated"}, status=status.HTTP_403_FORBIDDEN)
            login(request, user)
            ud = UserDetails.objects.get(user=user)
            user_serializer = UserSerializer(user)
            userdetails_serializer = UserDetailSerializer(ud)
            if ud.account_type == "Individual":
                individual_serializer = IndividualSerializer(
                    ud.individual)

                return Response({"message": "Login Successful",
                                "kyc-status": ud.individual.get_kyc_status(),
                                 'wallet-balance': ud.wallet.get_balance(),
                                 "user": user_serializer.data,
                                 "user-details": userdetails_serializer.data,
                                 "user-individual-details": individual_serializer.data,
                                 "token": {"refresh": str(RefreshToken.for_user(user)),
                                            "access": str(RefreshToken.for_user(user).access_token)}},
                                status=status.HTTP_200_OK)
            elif ud.account_type == "Business":
                business_serializer = BusinessSerializer(
                    ud.business)
                return Response({"message": "Login Successful",
                                'wallet-balance': ud.wallet.get_balance(),
                                 "user": user_serializer.data,
                                 "user-details": userdetails_serializer.data,
                                 "user-business-details": business_serializer.data,
                                 "token": {"refresh": str(RefreshToken.for_user(user)),
                                            "access": str(RefreshToken.for_user(user).access_token)}
                                 },
                                status=status.HTTP_200_OK)
        else:
            return Response({"message": "Wrong Email or Password"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return HttpResponse("Method not allowed")


@csrf_exempt
def logout_user(request):
    if request.method == "POST":
        body = json.loads(request.body)
        email = body['email']
        logout(request)
        user_data = {
            "email": email,
            "message": "logged out successful"
        }
        return JsonResponse(user_data)
    else:
        return "Method not allowed"


@csrf_exempt
@api_view(('POST', 'PUT', 'GET'))
@permission_classes((IsAuthenticated, ))
def pin(request):
    if request.method == 'POST':

        serializer = PinSerializer(data=request.data)
        if serializer.is_valid() is not True:
            return error_response(data=serializer._errors, status=400)

        data = serializer.data
        instance = UserDetails.objects.get(uuid=data['uuid'])

        if instance.pin is None:
            instance.pin = hashlib.sha256(data['pin'].encode()).hexdigest()
            instance.save()
            return success_response(message='Pin saved successful')
        else:
            return error_response(message='pin already exist', status=200)
    if request.method == 'PUT':
        serializer = PinUpdateSerializer(data=request.data)
        if serializer.is_valid() is not True:
            return error_response(data=serializer._errors, status=400)

        data = serializer.data
        instance = UserDetails.objects.get(uuid=data['uuid'])

        old_pin = hashlib.sha256(data['old_pin'].encode()).hexdigest()
        new_pin = hashlib.sha256(data['new_pin'].encode()).hexdigest()

        if old_pin != instance.pin:
            return error_response(message='old pin does not match', status=200)
        instance.pin = new_pin
        instance.save()
        return success_response(message='Pin Updated')
    if request.method == "GET":
        instance = UserDetails.objects.get(user=request.user)
        if instance.pin is None:
            return success_response(data={'status': False}, message='Pin status')
        else:
            return success_response(data={'status': True}, message='Pin status')


class UserDetail(viewsets.ModelViewSet):

    queryset = UserDetails.objects.all()
    serializer_class = UserDetailSerializer
    lookup_field = 'uuid'

    def get_serializer_class(self):
        serializer_class = self.serializer_class

        if self.request.method == 'PUT':
            serializer_class = UpdateUserDetailsSerializers
        return serializer_class

    def retrieve(self, request, *args, **kwargs):
        ud = self.get_object()
        serializer = self.get_serializer(ud)
        return Response({'status': 'success', 'message': 'user details', 'data': serializer.data}, status.HTTP_200_OK)


class EmployeeViewSet(viewsets.ModelViewSet):

    queryset = UserDetails.objects.all()
    serializer_class = EmployeeSerializer
    lookup_field = 'uuid'

    def get_object(self):
        ud = UserDetails.objects.get(uuid=self.kwargs.get('uuid'))
        return get_object_or_404(Employee, individual=ud.individual)

    def retrieve(self, request, *args, **kwargs):
        employee = self.get_object()
        serializer = self.get_serializer(employee)
        return Response(
            {'status': 'success', 'message': 'employee details', 'data': serializer.data},
            status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        ud = UserDetails.objects.get(uuid=request.data['uuid'])
        try:
            employee = Employee.objects.create(individual=ud.individual)
        except IntegrityError:
            return Response({'status': 'failed', 'message': 'employee exists'}, status.HTTP_200_OK)
        serializer = self.get_serializer(employee, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'status': 'success', 'message': 'employee updated', 'data': serializer.data},
            status.HTTP_200_OK)


class UserDetailViewSet(viewsets.ModelViewSet):

    """
    A simple ViewSet for viewing and editing accounts.
    """
    queryset = UserDetails.objects.select_related("user").all()
    serializer_class = UserDetailSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]


class IndividualCollection(viewsets.ModelViewSet):
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer

    def list(self, request, uuid):
        ud = get_object_or_404(UserDetails, uuid=uuid)
        individual = get_object_or_404(Individual, user=ud)
        firstname = ud.user.first_name
        lastname = ud.user.last_name
        email = ud.user.email
        bvn = ud.bvn
        identification_number = individual.identification_number
        identification_type = individual.identification_type
        return Response({"message": [
            {
                "firstname": firstname,
                "lastname": lastname,
                "email": email,
                "bvn": bvn,
                identification_type: identification_number
            }
        ]})


class BusinessCollection(viewsets.ModelViewSet):
    queryset = Business.objects.all()
    serializer_class = BusinessSerializer

# Exposed API to create entry in crm FOR PARTNERS


@ api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def create_user_crm(request):
    body = json.loads(request.body)
    register_in_crm = CRM.create_crm(request=request,
                                     bvn=body['bvn'], email=body['email'],
                                     birthdate=body['date_of_birth'],
                                     first_name=body['first_name'],
                                     middle_name=body['middle_name'],
                                     last_name=body['last_name'],
                                     phone=body['phone'],
                                     address=body['address'])
    if 'globalisationMessageCode' in register_in_crm:
        if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
            return Response({
                "message": "User Email Address Already Exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.externalId':
            return Response({
                "message": "User BVN Already Exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.mobileNo':
            return Response({
                "message": "User Phone Number Already Exists"
            }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            "message": register_in_crm['globalisationMessageCode']
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        clientId = register_in_crm['clientId']
        resourceId = register_in_crm['resourceId']
        savingsId = register_in_crm['savingsId']
        return Response({
            "message": "User Created Successfully",
            "data": {
                "clientId": clientId,
                "resourceId": resourceId,
                "savingsId": savingsId
            }
        }, status=status.HTTP_200_OK)

# Exposed API to create entry in crm


@ api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def create_user_crm2(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    if ud.account_type == "Individual":
        register_in_crm = CRM.create_crm(request=request,
                                         bvn=ud.individual.identification_number, email=ud.user.email,
                                         birthdate=ud.individual.dob or date.today(),
                                         first_name=ud.user.first_name,
                                         middle_name=ud.user.last_name,
                                         last_name=ud.user.last_name,
                                         phone=ud.phone,
                                         address=ud.individual.address or "Lagos")
        if 'globalisationMessageCode' in register_in_crm:
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
                return Response({
                    "message": "User Email Address Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.externalId':
                return Response({
                    "message": "User BVN Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.mobileNo':
                return Response({
                    "message": "User Phone Number Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "message": register_in_crm['globalisationMessageCode']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            clientId = register_in_crm['clientId']
            resourceId = register_in_crm['resourceId']
            savingsId = register_in_crm['savingsId']
            return Response({
                "message": "User Created Successfully",
                "data": {
                    "clientId": clientId,
                    "resourceId": resourceId,
                    "savingsId": savingsId
                }
            }, status=status.HTTP_200_OK)
    else:
        register_in_crm = CRM.create_crm(request=request,
                                         bvn=ud.business.shareholder1_identification_number, email=ud.user.email,
                                         birthdate=date.today(),
                                         first_name=ud.user.first_name,
                                         middle_name=ud.user.last_name,
                                         last_name=ud.user.last_name,
                                         phone=ud.phone,
                                         address=ud.business.office_address or "Lagos")
        if 'globalisationMessageCode' in register_in_crm:
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
                return Response({
                    "message": "User Email Address Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.externalId':
                return Response({
                    "message": "User BVN Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.mobileNo':
                return Response({
                    "message": "User Phone Number Already Exists, Please contact admin to create loan"
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                "message": register_in_crm['globalisationMessageCode']
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            clientId = register_in_crm['clientId']
            resourceId = register_in_crm['resourceId']
            savingsId = register_in_crm['savingsId']
            return Response({
                "message": "User Created Successfully",
                "data": {
                    "clientId": clientId,
                    "resourceId": resourceId,
                    "savingsId": savingsId
                }
            }, status=status.HTTP_200_OK)


# ###### KYC SYSTEM #############

# ONBOARDING INDIVIDUAL
class UserOnboardViewSet(viewsets.ModelViewSet):
    """
    API for onboarding users to PNGME and Creating monnify Reserved Account
    """
    queryset = Individual.objects.all()
    serializer_class = IndividualSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            ud = UserDetails.objects.get(uuid=request.data['uuid'])
        except KeyError:
            return Response({'message': 'invalid UUID'}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(UserDetails, uuid=request.data['uuid'])
        serializer = UserDetailSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        body = json.loads(request.body)
        user = get_object_or_404(UserDetails, user=request.user)
        individual = get_object_or_404(Individual, user=user)
        individual.identification_type = body['identification_type']
        individual.identification_number = body['identification_number']
        individual.onboarded = True
        individual.save()
        return Response({"status": "success",
                         "onboarded": True,
                         "message": "Onboarded Successfully"}, status=status.HTTP_201_CREATED)


class OnboardIndividual(APIView):

    def get(self, request, *args, **kwargs):
        try:
            ud = UserDetails.objects.get(uuid=request.data['uuid'])
        except KeyError:
            return Response({'message': 'invalid UUID'}, status=status.HTTP_400_BAD_REQUEST)
        instance = get_object_or_404(UserDetails, uuid=request.data['uuid'])
        serializer = UserDetailSerializer(instance)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = get_object_or_404(UserDetails, user=request.user)
        individual = get_object_or_404(Individual, user=user)
        individual.identification_type = data['identification_type']
        individual.identification_number = data['identification_number']
        user.bvn = data['identification_number']
        user.phone = data['phone']
        individual.onboarded = True
        individual.save()
        user.save()
        return success_response(message="Onboarded Successfully", data=True, status=status.HTTP_201_CREATED)

# ONBOARD BUSINESS


@ api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated, ])
def onboardBusiness(request, uuid, *args, **kwargs):
    ud = UserDetails.objects.get(uuid=uuid)
    business = Business.objects.get(user=ud)
    body = json.loads(request.body)
    serializer = VerifySerializer(data=body)
    serializer.is_valid(raise_exception=True)
    body = serializer.data
    if request.method == 'POST':
        business.business_name = body['company_name']
        business.onboarded = True
        business.rc_number = body['rc_number']
        business.save()
        Verification.youverify_business(body['company_name'])
        return Response({"status": True,
                         "message": "Successful, we are currently reviewing your business".format(body["company_name"]),
                         "onboarded": business.onboarded}, status=status.HTTP_200_OK)

# GET INDIVIDUAL KYC SCORE


@ api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def getKyc(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    individual = get_object_or_404(Individual, user=ud)
    return Response({"message": individual.get_kyc_status()})

# VALIDATE BVN


@ api_view(['POST'])
def validateBVN(request):
    body = json.loads(request.body)
    bvn = body['bvn']
    first_name = body['first_name']
    last_name = body['last_name']
    validate_bvn = Verification.youverify_bvn(bvn, first_name, last_name)
    return Response({"message": validate_bvn})

# GET INDIVIDUAL KYC Form


@ api_view(['GET'])
@permission_classes([IsAuthenticated])
def getKycForm(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    individual = get_object_or_404(Individual, user=ud)
    return Response({"message": individual.filled_kyc_form()})

# GET BUSINESS KYC STATUS


@ api_view(['GET'])
@permission_classes([IsAuthenticated])
def getBusinessKyc(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    individual = get_object_or_404(Business, user=ud)
    return Response({"message": individual.is_onboarded()})


@ api_view(['POST'])
@parser_classes([parsers.MultiPartParser])
@permission_classes([IsAuthenticated])
def getBusinessKyc(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    individual = get_object_or_404(Business, user=ud)
    return Response({"message": individual.is_onboarded()})


@ api_view(['POST', 'GET', 'PUT'])
@permission_classes([IsAuthenticated])
def verify_kyc2(request):
    if request.method == 'POST':
        ud = UserDetails.objects.get(user=request.user)
        individual = Individual.objects.get(user=ud)
        serializer_data = VerifyKYCSerializer(data=request.data)
        serializer_data.is_valid(raise_exception=True)
        data = serializer_data.data

        Individual.objects.filter(user=ud).update(
            identification_number=data['identification_number'],
            identification_type=data['identification_type'],
            address=data['address'],
            lga=data['lga'],
            state=data['state'],
            dob=data['dob'],
            gender=data['gender']
        )
        NextOfKin.objects.update_or_create(
            individual=individual,
            defaults={'phone': data['nok_phone'],
                      'name': data['nextofkin_name'],
                      'email': data['nextofkin_email']})
        Employee.objects.update_or_create(
            individual=individual,
            defaults={'company_name': data['companyName'],
                      'start_date': data['employeeStartDate'],
                      'net_income': data['NetMonthlyIncome'],
                      'email': data['companyemail'],
                      'address': data['employeraddress']})
        if individual.address_verification_status == 'NOT VERIFIED':
            response = Verification.youverify_setup(
                idnum=data['identification_number'],
                idtype=data['identification_type'],
                lastname=ud.user.last_name, firstname=ud.user.first_name, dob=data['date_of_birth'])
            response = json.loads(response)
            if response['status_code'] == 200:
                try:
                    individual.photo_link = response["data"]['response']["photo"]
                    wrong_date = response["data"]['response']["dob"].split("-")
                    datetime_object = datetime.strptime(wrong_date[1], "%b")
                    month_number = datetime_object.month
                    wrong_date[1] = month_number
                    new_date = "{0}-{1}-{2}".format(
                        wrong_date[2], wrong_date[1], wrong_date[0])
                    date = datetime.strptime(
                        new_date, '%y-%m-%d').strftime('%Y-%m-%d')
                    individual.dob = date
                    individual.save()
                except:
                    pass

        client_details = get_client_id(data['identification_number'], data['phone'])
        if client_details == None:
            register_in_crm = CRM.create_crm(request=request,
                                             bvn=data['identification_number'], email=ud.user.email,
                                             birthdate=individual.dob,
                                             first_name=ud.user.first_name,
                                             middle_name=ud.user.last_name,
                                             last_name=ud.user.last_name,
                                             phone=data['phone'],
                                             address=individual.address)
            if register_in_crm["globalisationMessageCode"] == 'error.msg.client.duplicate.email':
                individual.crm_clientId = 0
                individual.save()
            else:
                individual.crm_clientId = register_in_crm['clientId']
                individual.save()
        else:
            individual.crm_clientId = client_details
            individual.save()

        return Response({"message": 'KYC completed successfully'})


class VerifyKYC(APIView):

    def get(self, request):
        ud = UserDetails.objects.get(user=request.user)
        individual = Individual.objects.get(user=ud)
        individual_serializer = IndividualSerializer(individual)

        data = {
            "individual": individual_serializer.data,
        }
        return success_response(message="User KYC details", data=data)

    def post(self, request):
        ud = UserDetails.objects.get(user=request.user)
        serializer = VerifyKYCSerializer(data=request.data)
        if serializer.is_valid() is False:
            error_response(status=400, data=serializer._errors)
        data = serializer.data

        # update individual
        photo_link = upload_image(data['image'], ud.uuid)
        individual_data = {'identification_type': data['identification_type'],
                           'lga': data['lga'], 'address': data['address'],
                           'state': data['state'], 'dob': data['date_of_birth'],
                           'gender': data['gender'], 'crm_clientId': 0, 'crm_resourceId': 0,
                           'crm_savingsId': 0, 'filled_kyc': True, 'photo_link': photo_link
                           }
        Individual.objects.filter(user=ud).update(**individual_data)
        return success_response(message='KYC completed successfully')


@ api_view(['POST', 'GET', 'PUT'])  # remove excesses http methods
@permission_classes([IsAuthenticated])
def business_kyc(request, uuid):
    data = request.data
    ud = UserDetails.objects.get(uuid=uuid)
    business = Business.objects.get(user=ud)
    serializer = BusinessSerializer(business, data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(
        {'status': 'success', 'onboard': business.is_onboarded(),
         'data': serializer.data},
        status=status.HTTP_200_OK)

# verify an address


@ api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def verifyAddress(request):
    body = json.loads(request.body)
    uuid = body["uuid"]
    ud = get_object_or_404(UserDetails, uuid=uuid)
    if ud.account_type == "Individual":
        individual = Individual.objects.get(user=ud)
        photo = body['photo']
    if ud.account_type == "Business":
        business = Business.objects.get(user=ud)
        business_name = business.company_name
    firstname = ud.user.first_name
    lastname = ud.user.last_name
    email = ud.user.email
    street = body["address"]
    lga = body["lga"]
    state = body["state"]
    phone = body['phone']
    # create candidate
    candidate_id = Verification.youverify_candidate(firstname, lastname, email, phone)
    if ud.account_type == "Business":
        address = Verification.businessAddressVerification(candidate_id, business_name, business.rc_number,
                                                           email, phone, street, state, lga)
        if address == 200:
            business.address_verification_status = "VERIFYING"
            business.save()
            return Response(
                {"status": "success", "message": "Address Verification submitted"},
                status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": address
            }, status=status.HTTP_403_FORBIDDEN)
    if ud.account_type == "Individual":
        address = Verification.addressVerification(candidate_id, street, state, lga, photo)
        if address == 200:
            ud.individual.lga = lga,
            ud.individual.addressVerification = street,
            ud.individual.state = state
            ud.individual.address_verification_status = "VERIFYING"
            individual.save()
            return Response(
                {"status": "success", "message": "Address Verification submitted"},
                status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": address['errors']
            }, status=status.HTTP_403_FORBIDDEN)

# Address verification webhook


@ api_view(['POST'])
def addressWebhook(request):
    webhook = json.loads(request.body)
    try:
        email = webhook['data']['report']['candidate']['email']
        ud = User.objects.get(email=email)
        user = UserDetails.objects.get(user=ud)
        print(user)
    except:
        return Response({"message": "failed"})
    verification_status = webhook['data']['report']['task_status']
    if verification_status == "VERIFIED":
        Individual.objects.filter(user=user).update(
            address_verification_status="VERIFIED")
        return Response({"message": "Successful Verification"})

# get status


@ api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def guarantor(request):
    ud = UserDetails.objects.get(user=request.user)
    if request.method == 'POST':
        serializer = GuarantorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        data.pop('user')
        # if ud.account_type == "Individual":
        #     bvn=ud.individual.identification_number
        #     phone = ud.phone
        #     dob = ud.individual.dob
        #     address = ud.individual.address
        # else:
        #     bvn= ud.business.shareholder1_identification_number
        #     phone = ud.phone
        #     dob = date.today()
        #     address = ud.business.office_address

        # baseurl = config("CRM_PROD_URL")+"/integration-service/api/v1/customers/{}".format(get_client_id(bvn, phone))
        # data = {
        #     "emailAddress" : "makavelidason@gmail.com",
        #     "lastname" : "Sowunmi",
        #     "mobileNo" : "08136277230",
        #     "bvn" : 2223334567,
        #     "firstname" : "Wunmi"
        # }

        obj, created = Guarantor.objects.update_or_create(user=ud, defaults=data)
        if created:
            return Response({"message": "Guarantor Created", "data": obj})
        else:
            return Response({"message": "Guarantor Updated"})
    if request.method == 'GET':
        guarantor = Guarantor.objects.get(user=ud)
        serializer = GuarantorSerializer(guarantor)
        data = serializer.data
        return Response({"message": data})


@ api_view(['GET'])
@permission_classes([IsAuthenticated, ])
def addressStatus(request, uuid):
    ud = get_object_or_404(UserDetails, uuid=uuid)
    return Response({"message": ud.individual.address_verification_status})


class IndividualDocumentViewset(viewsets.ModelViewSet):

    queryset = IndividualDocuments.objects.all()
    serializer_class = IndividualDocumentSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'put']

    def list(self, request, user, **kwargs):
        document = IndividualDocuments.objects.filter(user=request.user)
        serializer = IndividualDocumentSerializer(document)
        return Response(serializer.data)


class BusinessDocumentViewset(viewsets.ModelViewSet):

    queryset = BusinessDocument.objects.all()
    serializer_class = BusinessDocumentSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def list(self, request, user, **kwargs):
        ud = UserDetails.objects.get(user=request.user)
        document = BusinessDocument.objects.filter(user=ud.uuid)
        serializer = BusinessDocumentSerializer(document)
        return Response(serializer.data)


class VerifyAddressViewset(viewsets.ModelViewSet):

    queryset = VerifyAddress.objects.all()
    serializer_class = IndividualSerializer

    def create(self, request):
        body = json.loads(request.body)
        uuid = body["uuid"]
        ud = get_object_or_404(UserDetails, uuid=uuid)
        individual = Individual.objects.get(user=ud)
        street = body["address"]
        lga = body["lga"]
        state = body["state"]
        firstname = ud.user.first_name
        lastname = ud.user.last_name
        email = ud.user.email
        phone = body['phone']
        # create candidate
        candidate_id = Verification.youverify_candidate(
            firstname, lastname, email, phone)
        address = Verification.addressVerification(
            candidate_id, street, state, lga, ud.individual.photo_link)
        print(address)
        if address == 200:
            ud.individual.lga = lga,
            ud.individual.addressVerification = street,
            ud.individual.state = state
            ud.individual.address_verification_status = "VERIFYING"
            individual.save()
            return Response(
                {"status": "success", "message": "Address Verification submitted"},
                status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "failed",
                "message": address['errors']
            }, status=status.HTTP_403_FORBIDDEN)
