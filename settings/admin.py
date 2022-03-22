from django.contrib import admin

from .models import BusinessSettings, IndividualSettings

# Register your models here.
admin.site.register(BusinessSettings)
admin.site.register(IndividualSettings)
