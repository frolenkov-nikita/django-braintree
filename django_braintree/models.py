import logging
from decimal import Decimal, DecimalException

from django.db import models
from django.conf import settings

from braintree import Transaction


class UserVaultManager(models.Manager):
    def get_user_vault_instance_or_none(self, user):
        """Returns a vault_id string or None"""
        qset = self.filter(user=user)

        if not qset.exists():
            return None

        # for compatibility return first result even if we have many
        return qset[0]

    def is_in_vault(self, user):
        return True if self.filter(user=user) else False

    def charge(self, user, vault_id=None):
        """If vault_id is not passed this will assume that there is only one instane of user and vault_id in the db."""
        assert self.is_in_vault(user)
        if vault_id:
            user_vault = self.get(user=user, vault_id=vault_id)
        else:
            user_vault = self.get(user=user)


class UserVault(models.Model):
    """Keeping it open that one user can have multiple vault credentials, hence the FK to User and not a OneToOne."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    vault_id = models.CharField(max_length=64, unique=True)

    objects = UserVaultManager()

    def __unicode__(self):
        return self.user.username

    def charge(self, amount):
        """
        Charges the users credit card, with he passed $amount, if they are in the vault. Returns the payment_log instance
        or None (if charge fails etc.)
        """
        # TODO: refactor! This is not how such operations should be done.
        amount = Decimal(amount)
        try:
            result = Transaction.sale(
                {
                    'amount': amount.quantize(Decimal('.01')),
                    'customer_id': self.vault_id,
                    'options': {
                        'submit_for_settlement': True
                    }
                }
            )

            if result.is_success:
                # create a payment log
                payment_log = PaymentLog.objects.create(user=self.user,
                                        amount=amount,
                                        transaction_id=result.transaction.id)
                return payment_log
            else:
                logging.error("Bad braintree response %s" % result)
                raise Exception("Logical error in CC transaction")
        except Exception, e:
            logging.error("Failed to charge $%s to user:"
                " %s with vault_id: %s error was %s" % (amount, self.user,
                                                     self.vault_id, e))
            return None

class PaymentLog(models.Model):
    """
    Captures raw charges made to a users credit card. Extra info related to this payment should be a OneToOneField
    referencing this model.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    timestamp = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=128)

    def __unicode__(self):
        return '%s charged $%s - %s' % (self.user, self.amount, self.transaction_id)
