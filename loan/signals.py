from django.db.models.signals import post_save
from wallet.models import Wallet
from .models import Loan
from wallet.webhooks import updateBalance


def update_wallet(sender, instance, created, **kwargs):
    if created:
        if instance.status == 'Completed':
            if Wallet.objects.filter(user=instance).exists():
                userWallet = Wallet.objects.get(user=instance)
                increment = float(instance.amount)
                currBalance = userWallet.balance
                userWallet.lastBalance = currBalance
                userWallet.balance = updateBalance(currBalance, increment)
                userWallet.save()
            if not Wallet.objects.filter(user=instance).exists():
                Wallet.objects.create(user=instance, balance=instance.amount, )


post_save.connect(update_wallet, sender=Loan)
