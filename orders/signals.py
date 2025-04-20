import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from .models import Order
from clients.models import Account

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def on_order_confirmed(sender, instance, created, **kwargs):

    if instance.status == "confirmed":
        try:
            with transaction.atomic():

                account = Account.objects.get(client=instance.client)

                if (
                    instance._state.adding is False
                    and not instance.stock_status == "confirmed"
                ):
                    account.add_debt(instance.total)

                    Order.objects.filter(id=instance.id).update(
                        stock_status="confirmed"
                    )

                    for item in instance.items.all():
                        item.product.adjust_stock(item.quantity)

        except Exception as e:
            logger.error(f"Error en on_order_confirmed: {e}")
