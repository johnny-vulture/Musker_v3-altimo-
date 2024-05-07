from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Profile,  Challenge, Cryptocurrency, Notification, ChallengeInvoice, Portfolio
# Unregister Groups
admin.site.unregister(Group)

# Mix Profile info into User info


class ProfileInline(admin.StackedInline):
    model = Profile

# Extend User Model


class UserAdmin(admin.ModelAdmin):
    model = User
    # Just display username fields on admin page
    fields = ["username"]
    inlines = [ProfileInline]


# Unregister initial User
admin.site.unregister(User)

# Reregister User and Profile
admin.site.register(User, UserAdmin)
# admin.site.register(Profile)


# Register Challenges
admin.site.register(Challenge)

# Register Cryptocurrency
admin.site.register(Cryptocurrency)

# Register notification
admin.site.register(Notification)

# Register Invoice
admin.site.register(ChallengeInvoice)

# Register portfolio
admin.site.register(Portfolio)
