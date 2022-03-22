from django.urls import path
from rest_framework.authtoken import views as auth
from django.conf.urls import url, include
from . import views, webhooks
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'details',
                views.WalletViewSet, basename="user-wallet")
router.register(r'transaction/(?P<uuid_id>[^/]+)', views.TransactionViews,
                basename="transaction")
router.register(r'witmono/(?P<uuid_id>[^/]+)',
                views.WitMonoViews, basename="get-moono")
router.register(r'witmono', views.WitMonoViews, basename="witmono-account")

urlpatterns = [
    url(r'^', include(router.urls)),
    path('notifyTransaction', webhooks.transactionHook, name="notifyTransaction"),
    path('fundWallet/initiate/',
         views.FundWallet.as_view(), name='fundWallet initiate'),
    path('walletbalance/<str:uuid>', views.Balance, name="get_balance"),
    path('getallbanks', views.getbanks, name="getbanks"),
    path('reserved-account/<str:uuid>/',
         views.createAccount, name="createAccount"),
    path('getreservedaccount/<str:uuid>/',
         views.getReservedAccount, name="getReservedAccount"),
    path('credit/',
         views.fund_wallet, name="fund wallet"),
    path('banktransfer', views.transfer_to_bank, name="bank transfer"),
    path('settlement_notif', views.reservedAccountWebhook,
         name="reservedAccountWebhook"),
    path('verify_bankaccount', views.verify_bankaccount, name=' bank verification')
]
