from django.conf.urls import url, include
from django.urls import path
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'vendor', views.VendorViewSet, basename="vendor")
router.register(r'customers', views.CustomerViewSet, basename="customers")
router.register(r'products',
                views.ProductViewSet, basename="product")
router.register(r'service',
                views.ServiceViewSet, basename="service")
router.register(r'asset', views.AssetViewSet, basename="asset")
router.register(r'liability',
                views.LiabilityViewSet, basename="liablility")
# router.register(r'user_loan', views.LoanViewSet, basename="user-loan")

urlpatterns = [
    url(r'^', include(router.urls)),
    path('create/', views.CreateAccount, name='create account'),
    path('update/', views.update_account, name='update account'),
    path('list/', views.ListAccount, name='retrieve accounts'),
    path('default-account/', views.DefaultAccount,
         name='create default accounts'),
    path('type-category/', views.TypesCategory,
         name='List of Type Category'),
    path('journal/', views.save_journal, name='save journal'),
    path('journal/list/', views.list_journal, name='list journals'),
    path('journal/delete/<uuid:uuid>/', views.delete_journal, name="delete journal"),
    path('create-invoice/', views.CreateInvoice, name='create invoice'),
    path('get-invoice/<uuid:uuid>/', views.getInvoice, name='get invoice'),
    path("send-invoice/", views.send_invoice, name='send invoice'),
    path('update-invoice/', views.update_invoice, name='update invoice'),
    path('all-invoice/', views.getallInvoice, name='get all invoice'),
]
