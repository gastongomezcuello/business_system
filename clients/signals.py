from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime
import random


from .models import Client, Account


def generate_account_number(client):

    random_part = str(random.randint(100000, 999999))

    current_year = str(datetime.now().year)[-2:]
    client_id = str(client.id).zfill(5)

    account_number = f"{random_part}{current_year}{client_id}"
    return account_number


@receiver(post_save, sender=Client)
def create_account(sender, instance, created, **kwargs):
    if created:
        account_number = generate_account_number(instance)
        Account.objects.create(client=instance, account_number=account_number)
