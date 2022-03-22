from .models import Ledger
from rest_framework.exceptions import APIException
from transaction.models import Transaction
from users.models import UserDetails
from django.core.exceptions import ObjectDoesNotExist


class LedgerError(APIException):
    status_code = 503
    default_detail = 'Service temporarily unavailable, try again later.'
    default_code = 'Ledger Error'


class TransactionCompleteHook:

    @staticmethod
    def credit(transaction_id):
        transaction_id = int(transaction_id)
        try:
            get_ledger = Ledger.objects.get(ledger_entity=transaction_id)
        except ObjectDoesNotExist:
            get_transaction = Transaction.objects.get(id=transaction_id)
            credit_amount = get_transaction.amount
            credit_amount = 0 if credit_amount < 0 else credit_amount

            credit_data = {
                'ledger_entity': get_transaction.id,
                'comment': 'LEGERED CREDIT WITH REFERENCE {0}'.format(get_transaction.reference),
                'type': get_transaction.type,
                'uuid': get_transaction.user.uuid,
                'amount': credit_amount
            }

            ledger = Ledger.objects.credit(**credit_data)
            ledger.save()
            return ledger

        if get_ledger is not None:
            raise LedgerError(detail='Transaction already ledgered')

    @staticmethod
    def debit(transaction_id):
        transaction_id = int(transaction_id)
        try:
            get_ledger = Ledger.objects.get(ledger_entity=transaction_id)
        except ObjectDoesNotExist:
            get_transaction = Transaction.objects.get(id=transaction_id)
            debit_amount = get_transaction.amount
            debit_amount = 0 if debit_amount < 0 else debit_amount

            debit_data = {
                'ledger_entity': get_transaction.id,
                'comment': 'LEGERED DEBIT WITH REFERENCE {0}'.format(get_transaction.reference),
                'type': get_transaction.transaction_type,
                'uuid': get_transaction.user.uuid,
                'amount': debit_amount
            }

            ledger = Ledger.objects.debit(**debit_data)
            ledger.save()
            return ledger

        if get_ledger is not None:
            raise LedgerError(detail='Transaction already ledgered')
