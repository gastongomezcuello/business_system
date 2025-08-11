from django.db.models.signals import post_save
from django.dispatch import receiver
from clients.utils.hashes import generate_numeric_hash
import random


from .models import Client, Account

print("✅ Signals importadas")


@receiver(post_save, sender=Client)
def set_client_code(sender, instance, created, **kwargs):
    if created:
        instance.code = generate_numeric_hash(instance.id)

        instance.save()


@receiver(post_save, sender=Client)
def create_account(sender, instance, created, **kwargs):
    if created:

        Account.objects.create(
            client=instance,
            account_number=("22" + instance.code + str(random.randint(1000, 9999))),
        )


@receiver(post_save, sender=Account)
def post_account_creation(sender, instance, created, **kwargs):
    if created:
        if instance.payments.exists():
            instance.last_payment_date = (
                instance.payments.order_by("-date").first().date
            )
