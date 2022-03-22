from services.crm import create_customer
from django.urls import path
from .views import (bank_transfer, bank_transfer_webhook, manual_transfer,getServices,validateCustomer, makeBill, InvestmentView)
from .crm import create_customer, create_loan, get_repayment, repay_loan, create_coporate_customer


urlpatterns = [
    path('transfer', bank_transfer, name='bank-transfer'),
    path('manual_transfer', manual_transfer, name='manual-transfer'),
    path('transfer-webhook', bank_transfer_webhook, name='bank-transfer-webhook'),
    path('create_investment/', InvestmentView.as_view(), name="investment"),
    path('investment/', InvestmentView.as_view(), name="investment"),
    path('get-bill-services/', getServices, name="getServices"),
    path('validate-customer-bill/', validateCustomer, name="validateCustomer"),#not working
    path('pay-bill/', makeBill, name="makeBill"),
    path('create-customer/', create_customer, name="create-customer"),
    path('create-coporate/', create_coporate_customer, name="create-coporate"),
    path('create-loan/', create_loan, name="create_loan"),#not working 
    path('get-repayment/<uuid:uuid>/', get_repayment, name="get_repayment"),
    path('repay-loan/', repay_loan, name="repay_loan")
]
