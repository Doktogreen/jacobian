from django.urls import path
from rest_framework.authtoken import views as auth
from django.conf.urls import url, include
from users.models import Guarantor
from . import views
from services.views import check_pin
from rest_framework import routers

user_kyc = views.UserOnboardViewSet.as_view({
    "post": "user_kyc"
})

router = routers.DefaultRouter()
router.register(r'onboard_user', views.UserDetailViewSet,
                basename="onboard-user")
router.register(r'user-details/(?P<uuid_id>[^/]+)', views.UserDetail,
                basename="user-details")
router.register(r'employee-details', views.EmployeeViewSet,
                basename="employee-details")
# router.register(r'onboard', views.UserOnboardViewSet, basename="onboard") #in use currently for individual-onboard
router.register(r'individual/(?P<uuid>[^/]+)', views.IndividualCollection,
                basename="individual")
router.register(r'business', views.BusinessCollection, basename="business")
router.register(r'uploaddocuments/(?P<user>[^/]+)', views.IndividualDocumentViewset, basename="individualdocument")
router.register(r'uploadcertificates/(?P<user>[^/]+)', views.BusinessDocumentViewset, basename="businessdocumnet")
router.register(r'verify_address', views.VerifyAddressViewset, basename="verifyaddress")

urlpatterns = [
    path('', views.RegisterUser.as_view(), name="register"), 
    url(r'^', include(router.urls)),
    #Admin Routes
    path('users', views.get_users, name="index"),
    #User Routes

    path('login', views.login_user, name='login'),
    path('support/', views.support_email, name='support'),
    path('addresswebhook/', views.addressWebhook, name='addressWebhook'),
    path('validate_bvn/', views.validateBVN, name="validate_loan"),
    path('verify-KYC/', views.VerifyKYC.as_view(), name='verifyKYC'), 
    path('onboard/', views.OnboardIndividual.as_view(), name='onboard'),
    path('create_customer/', views.create_user_crm, name='createCustomer'), 
    path('create-loan-customer/<uuid:uuid>/', views.create_user_crm2, name='createCustomer'), 
    path('get-kyc/<uuid:uuid>/', views.getKyc, name='getKyc'),
    path('get-kyc-status/<uuid:uuid>/', views.getKycForm, name='getKycForm'),
    path('get-business-kyc/<uuid:uuid>/', views.getBusinessKyc, name='getBusinessKyc'),
    path('user-kyc', user_kyc, name='verifyKYC'),
    path('business-KYC/<uuid:uuid>/', views.business_kyc, name='businessKYC'),
    path('onboardBusiness/<uuid:uuid>/',
         views.onboardBusiness, name='onboardBusiness'),
    path('logout', views.logout_user, name='logout'),
    path('reset_password', views.reset_password, name='register'),
    path('verify_reset_password', views.verify_reset_password, name='verify_reset_password'),
    path('api-token-auth', auth.obtain_auth_token),
    path('set-pin/', views.pin, name='pin'),#done
    path("verifyAddress/", views.verifyAddress, name="verify_address"),
    path("statusAddress/<uuid:uuid>/", views.addressStatus, name="address_status"),
    path('verify-pin/', check_pin, name='verify-pin'),#done
    path('guarantor/', views.guarantor, name='guarantor')
]
