from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Register_Client)
admin.site.register(Balance)
admin.site.register(Identity)
admin.site.register(Income)
admin.site.register(Transaction)