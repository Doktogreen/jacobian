from django.urls import path
from . import views
from rest_framework import routers
from django.conf.urls import url, include

router = routers.DefaultRouter()
router.register(r'banktransactions/(?P<uuid_id>[^/]+)', views.BankTransactions, basename="bank-transaction")
urlpatterns = [
    url(r'^', include(router.urls)),

]
