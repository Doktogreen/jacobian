from django.contrib import admin
from .models import Wallet, ReservedAccounts, WitMono, AccountTransaction


# Register your models here.
class WalletAdmin(admin.ModelAdmin):
    list_display=("id", "wallet_id", "user_email", "balance", "status")
    list_display_links = ['user_email']
    search_fields = ["id", "wallet_id"]
    # fieldsets = [
    #     ('Current Amount(only Credit):',{'fields':['balance']}),
    #     ('Transaction Type:',{'fields':['debit_or_credit']}),
    #     ('Transaction Amount:',{'fields':['transaction_amount']}),
    #     ('Current Amount(only Credit):',{'fields':['curr_available_amount_if_credit_row']}),
    #     ('Remarks:',{'fields':['remarks']}),
    #     ('Transaction Unique ID:',{'fields':['transaction_method_record_unique_id']}),
    #     ('Transaction Time:',{'fields':['transaction_time']}),
    #     ('Expiry Time:',{'fields':['expiry_time_of_credited_amount']}),
    #     ('Linked Record ID',{'fields':['wallet_debit_record2wallet_credit_record']}),
    #     ('Store ID:',{'fields':['wallet2store_details']}),
    #     ('HMAC/CHECKSUM:',{'fields':['hmac_or_checksum']}),
    #     ('Status(0 --> Not deleted, 1 --> Deleted ):',{'fields':['is_deleted']}),

    # ]


admin.site.register(Wallet, WalletAdmin)
admin.site.register(AccountTransaction)
admin.site.register(ReservedAccounts)
admin.site.register(WitMono)