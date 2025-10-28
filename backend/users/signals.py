from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from .utils import award_badge


@receiver(post_save, sender=User)
def check_early_adopter_badge(sender, instance, created, **kwargs):
    if created:
        total_users = User.objects.count()
        if total_users <= 100:
            award_badge(instance, 'early_adopter')
