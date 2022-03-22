from django.contrib import admin
from .models import *
# Register your models here.
class LoanAdmin(admin.ModelAdmin):
    list_display=("user", "amount", "amount_paid", "contract_status", "status")
admin.site.register(Loan, LoanAdmin)
admin.site.register(Repayment)
admin.site.register(Contract)
admin.site.register(CRMLoan)
