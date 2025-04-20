from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from .models import Profile

User = get_user_model()


@receiver(post_save, sender=User)
def set_admin_flag_and_create_email(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        if instance.is_superuser:

            instance.is_active = True
            instance.is_admin = True
            instance.is_seller = False
            instance.save()

            EmailAddress.objects.create(
                user=instance, email=instance.email, primary=True, verified=True
            )
