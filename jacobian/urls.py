
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/dashboard/',
         include(('dashboard.urls', "app_name"), namespace="dashboard")),
    path('api/users/', include(('users.urls', "app_name"), namespace="users")),
    path('api/wallet/', include(('wallet.urls', "app_name"), namespace="wallet")),
    path('api/transaction/', include(('transaction.urls', "app_name"), namespace="transaction")),
    path('api/loan/', include(('loan.urls', "app_name"), namespace="loan")),
    path('api/account/', include(('account.urls', "app_name"), namespace="account")),
    path('api/services/', include(('services.urls', "app_name"), namespace="services")),
    path('api/cards/', include(('cards.urls', "app_name"), namespace="cards")),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/settings/', include(('settings.urls', 'app_name'), namespace='settings')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
