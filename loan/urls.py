from django.conf.urls import url, include
from . import views, sign
from django.urls import path
from rest_framework import routers

router = routers.DefaultRouter()
# create different viewset
router.register(r'loans', views.LoansViewSet,
                basename="loans")  # create different viewset
router.register(r'contract/(?P<id>[^/]+)',
                views.ContractViewSet, basename="send-contract")
router.register(r'contracts', views.ContractsViewSet, basename="all-contracts")
router.register(r'user/(?P<id>[^/]+)',
                views.LoansViewSet, basename="userloans")
router.register(r'plans',
                views.RepaymentViews, basename="plans")
router.register(r'user_loan', views.LoanViewSet, basename="user-loan")

urlpatterns = [
    url(r'^', include(router.urls)),
    # path('loan_score/<int:pk>', views.load_score, name="loan-score"),
    path('principalAmount', views.predict_with_mono, name="principalAmount"),
    path('kyc/', views.KYC.as_view(), name='loan-kyc'),
    path('userLoan/<int:pk>', views.LoansViewSet, name="userLoan"),
    path('loan-webhook/', views.loan_webhook, name="loan_webhook"),
    path('loanPrediction/<uuid:uuid>',
         views.loan_prediction, name="loanPrediction"),
    path('calculate-loan-score/<uuid:uuid>',
         views.loanScore, name="calculate-score"),
    path('repay/', views.repayLoan, name="repay-loan"),
    path('testsign/', sign.test_sign, name="sign-loan"),
    # path('create_loan/', views.create_loan_crm, name="create-loan"), #loan creation for partners
    # path('create-loan/', views.create_loan_crm2, name="create-loan"),
    # path('repay_loan/', views.repay_loan_crm, name="repay-loan_crm"),
    # path('get_loan/<uuid:uuid>/', views.get_client_crm, name="get_client_crm"),
    # path('repayment_schedule/<str:id>/', views.get_repayment_crm, name="get_repayment_crm")
]
