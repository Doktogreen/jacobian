from django.conf.urls import url, include
from rest_framework import routers

from .views import (ClientRegistrationViewSet, BalanceViewSet, IncomeViewSet, IdentityViewSet,
TransactionViewSet, BankChartViewSet, WalletPieChartViewSet, WalletCategoryViewSet)


router = routers.DefaultRouter()
router.register(r'register_client', ClientRegistrationViewSet, basename="register_client")
router.register(r'check_balance', BalanceViewSet, basename="check_balance")
router.register(r'check_identity', IdentityViewSet, basename='identity')
router.register(r'check_income', IncomeViewSet)
router.register(r'check_transaction', TransactionViewSet),
router.register(r'bank-chart/(?P<uuid_id>[^/]+)', BankChartViewSet, basename="bank-chart"),
router.register(r'wallet-chart/(?P<uuid_id>[^/]+)', WalletPieChartViewSet, basename="wallet-chart"),
router.register(r'wallet-categories/(?P<uuid_id>[^/]+)', WalletCategoryViewSet, basename="wallet-categories")
urlpatterns = [
  url(r'^', include((router.urls, "app_name"), namespace="dashboard"))
]

# app_name = 'dashboard'