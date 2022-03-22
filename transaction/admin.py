from django.contrib import admin
from .models import Transaction, Ledger

# Register your models here.


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'reference', "status", "user",
                    "amount", "currency", "created_date")


class LedgerAdmin(admin.ModelAdmin):

    list_display = ('ledger_entity', 'transaction_type',
                    'amount', 'user', 'opening_balance', 'credit_date', 'is_test')

    readonly_fields = ('amount', 'ledger_entity_method',
                       'user_method', 'type_method', 'opening_balance_method', 'credit_date_method', 'is_test_method')

    def amount_method(self, obj):
        return obj.amount

    def ledger_entity_method(self, obj):
        return obj.ledger_entity

    def user_method(self, obj):
        return obj.user

    def type_method(self, obj):
        return obj.transaction_type

    def is_test_method(self, obj):
        return obj.is_test

    def opening_balance_method(self, obj):
        return obj.opening_balance

    def credit_date_method(self, obj):
        return obj.credit_date

    amount_method.short_description = 'amount'
    ledger_entity_method.short_description = 'ledger entity'
    user_method.short_description = 'user email'
    type_method.short_description = 'type'
    is_test_method.short_description = 'is_test'
    opening_balance_method.short_description = 'opening balance'
    credit_date_method.short_description = ' credit date'


admin.site.register(Ledger, LedgerAdmin)

admin.site.register(Transaction, TransactionAdmin)
