from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from musker.models import Challenge, Notification
from django.core.mail import EmailMessage, send_mail


@receiver(pre_save, sender=Challenge)
def challenge_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.pk:  # If the instance already exists (updating)
        # Check if the status has changed to accepted
        if instance.status == 'accepted':
            # Create a notification
            Notification.objects.create(
                sender=instance.sender, receiver=instance.receiver, match_date=instance.match_date)
    else:  # If the instance is being created
        pass  # No action needed for now


@receiver(post_save, sender=Challenge)
def challenge_post_save_receiver(sender, instance, created, *args, **kwargs):
    if not created:  # If the instance was updated (not created)
        # Check if the status has changed to rejected
        if instance.status == 'rejected':
            # Delete the challenge
            instance.delete()
