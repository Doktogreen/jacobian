from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Account)
admin.site.register(Customers)
admin.site.register(Vendor)
admin.site.register(Invoice)
# admin.site.register(Account)
