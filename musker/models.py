from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# create meep model


# Create A User Profile Model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    follows = models.ManyToManyField("self",
                                     related_name="followed_by",
                                     symmetrical=False,
                                     blank=True)

    date_modified = models.DateTimeField(User, auto_now=True)
    profile_image = models.ImageField(
        null=True, blank=True, upload_to="images/")

    profile_bio = models.CharField(null=True, blank=True, max_length=500)
    homepage_link = models.CharField(null=True, blank=True, max_length=100)
    facebook_link = models.CharField(null=True, blank=True, max_length=100)
    instagram_link = models.CharField(null=True, blank=True, max_length=100)
    linkedin_link = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return self.user.username


# Create the portfolio linked to a user and store the total value of the portfolio

class Portfolio(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='portfolios')
    total_value = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - Portfolio: {self.total_value}'

# Create Profile When New User Signs Up
# @receiver(post_save, sender=User)


def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user=instance)
        user_profile.save()
        # Have the user follow themselves
        user_profile.follows.set([instance.profile.id])
        user_profile.save()

        # Create a portfolio for the user
        portfolio = Portfolio(user=instance)
        portfolio.save()


post_save.connect(create_profile, sender=User)


class Challenge(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )

    sender = models.ForeignKey(
        User, related_name='sent_challenges', on_delete=models.CASCADE)
    # Assuming username can be maximum 150 characters
    receiver_username = models.CharField(max_length=150)
    receiver = models.ForeignKey(
        User, related_name='received_challenges', null=True, blank=True, on_delete=models.SET_NULL)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending')
    match_date = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.TextField(max_length=100, default='pending')
    loser = models.TextField(max_length=100, default='pending')

##############################################################################

# Create the Cryptocurrency model


class Cryptocurrency(models.Model):
    # here name is also the id of the cryptocurrency, so useful for API calls
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cryptocurrencies', null=True)
    id_from_api = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)
    current_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return f'{self.name} ({self.symbol})'


###################################################################

class Notification(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_notifications')
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_notifications')
    creation_date = models.DateTimeField(auto_now_add=True)
    match_date = models.DateTimeField(null=True)

    def __str__(self):
        return f'{self.sender} -> {self.receiver}: {self.creation_date}'

####################################################################


class ChallengeInvoice(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
    receiver_username_iv = models.TextField(max_length=100, default='pending')
    sender_username_iv = models.TextField(max_length=100, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    sender_Portfolio_init_price = models.IntegerField(
        default=None, null=True, blank=True)
    # sender_Portfolio_fin_price = models.IntegerField(default=None)

    receiver_Portfolio_init_price = models.IntegerField(
        default=None, null=True, blank=True)
    # receiver_Portfolio_fin_price = models.IntegerField(default=None)

    winner = models.TextField(max_length=100, default='pending')
    loser = models.TextField(max_length=100, default='pending')
