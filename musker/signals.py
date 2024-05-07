from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from musker.models import Challenge, Notification, ChallengeInvoice, Portfolio
from django.core.mail import EmailMessage, send_mail


@receiver(pre_save, sender=Challenge)
def challenge_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.pk:  # If the instance already exists (updating)
        # Check if the status has changed to accepted
        if instance.status == 'accepted':
            # Create a notification
            Notification.objects.create(
                sender=instance.sender, receiver=instance.receiver, match_date=instance.match_date)

            # Check and create portfolios if necessary
            if not instance.sender.portfolios.exists():
                sender_portfolio = Portfolio(user=instance.sender)
                sender_portfolio.save()

            if not instance.receiver.portfolios.exists():
                receiver_portfolio = Portfolio(user=instance.receiver)
                receiver_portfolio.save()

            # Create ChallengeInvoice
            ChallengeInvoice.objects.create(
                challenge=instance,
                receiver_username_iv=instance.receiver.username,
                sender_username_iv=instance.sender.username,
                sender_Portfolio_init_price=instance.sender.portfolios.first().total_value,
                receiver_Portfolio_init_price=instance.receiver.portfolios.first().total_value,
                winner='TBA',
                loser='TBA'
                # sender_Portfolio_fin_price=None,  # Set to None or another default value
                # receiver_Portfolio_fin_price=None,  # Set to None or another default value
            )
    else:  # If the instance is being created
        pass  # No action needed for now


"""
@receiver(pre_save, sender=Challenge)
def challenge_pre_save_receiver(sender, instance, *args, **kwargs):
    if instance.pk:  # If the instance already exists (updating)
        # Check if the status has changed to accepted
        if instance.status == 'accepted':
            # Create a notification
            Notification.objects.create(
                sender=instance.sender, receiver=instance.receiver, match_date=instance.match_date)
            # Create ChallengeInvoice
            ChallengeInvoice.objects.create(
                challenge=instance,
                receiver_username_iv=instance.receiver.username,
                sender_username_iv=instance.sender.username,
                sender_Portfolio_init_price=instance.sender.portfolios.first(
                ).total_value,  # accessing the first portfolio object
                receiver_Portfolio_init_price=instance.receiver.portfolios.first(
                ).total_value,  # accessing the first portfolio object
                winner='TBA',
                loser='TBA'
                # sender_Portfolio_fin_price=None,  # Set to None or another default value
                # receiver_Portfolio_fin_price=None,  # Set to None or another default value
            )
    else:  # If the instance is being created
        pass  # No action needed for now
"""


@receiver(post_save, sender=Challenge)
def challenge_post_save_receiver(sender, instance, created, *args, **kwargs):
    if not created:  # If the instance was updated (not created)
        # Check if the status has changed to rejected
        if instance.status == 'rejected':
            # Delete the challenge
            instance.delete()
