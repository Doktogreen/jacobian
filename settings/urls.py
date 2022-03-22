from django.urls import path
from .views import BusinessSettingsView, IndividualSettingsView, create_individual_settings, create_business_settings

urlpatterns = [
    #path('individual/', IndividualSettingsList.as_view(), name='individuals-settings'),
    path('individual/<uuid:uuid>/', IndividualSettingsView.as_view(), name='individual-settings'),
    path('business/<uuid:uuid>/', BusinessSettingsView.as_view(), name='business-settings'),
    path('individual/create', create_individual_settings, name='individual-settings'),
    path('business/create', create_business_settings, name='business-settings'),
    path('individual/',  IndividualSettingsView.as_view(), name="Individual settings"),
    path('business/',  BusinessSettingsView.as_view(), name="Business settings")

]
