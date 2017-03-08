import re
from django.http import HttpResponse
from django.contrib.auth.models import User
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email, user_username, user_field
from allauth.account.utils import valid_email_or_none, user_username, user_email, user_field
from allauth.account.adapter import get_adapter as get_account_adapter
from allauth.exceptions import ImmediateHttpResponse
from django.conf import settings
from home.models import *


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.is_authenticated():
            return '/'
        else:
            return '/'

    def populate_username(self, request, user):
        user.username = user.email
        user.save()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        # Normal AllAuth Stuff
        u = sociallogin.user
        u.set_unusable_password()
        u = sociallogin.user
        u.set_unusable_password()
        if form:
            get_account_adapter().save_user(request, u, form)
        else:
            get_account_adapter().populate_username(request, u)
        sociallogin.save(request)

        # Get email from social account
        email = str(sociallogin.user.email)

        # Prior to creation of User, a shadow user may exist in BOPS
        # as a UserProfile and associated PersonalData

        # Check if existing UserProfile exists for email coming from Google Auth
        if PersonalData.objects.filter(email=email):
            # Get the appropriate UserProfile
            pd = PersonalData.objects.get(email=email)
            userprofile_focus = UserProfile.objects.get(personal_data=pd)
            # Check if found UserProfile is already assigned to a user
            if userprofile_focus.user:
                # UserProfile is already hooked up.
                print('Warning: this userprofile is already set.')
                pass
            else:
                # Connect the user up in the Signup Adapter
                realuser = User.objects.get(email=email)
                userprofile_focus.user = realuser
                userprofile_focus.save()
        else:
            # This is a new employee, populate name from Google account
            realuser = User.objects.get(email=email)

            # Create UserProfile and Related Data
            new_personal_data = PersonalData.objects.create(first_name=u.first_name, last_name=u.last_name, email=email)
            new_personal_data.save()
            new_user_profile = UserProfile.objects.create(user=realuser, personal_data=new_personal_data)
            new_user_profile.save()
            # return u

    def pre_social_login(self, request, sociallogin):

        # Verify user is a BoutiqueAir.com email address
        email = str(sociallogin.user.email)
        email_parts = email.split('@')
        domain = email_parts[1].lower()
        if domain == settings.ALLOWED_DOMAIN:
            # User is allowed to enter
            pass
        else:
            # Tell the user they can't come in, consider redirecting them or offering a link here.
            raise ImmediateHttpResponse(HttpResponse('This site is for Boutique Air employees only.'))

        # Handle first Google logins from existing users
        # social account already exists, so this is just a login
        if sociallogin.is_existing:
            return

        # Try to associate an existing user with this account
        try:
            user = User.objects.get(email=email)
            # if it does, connect this new social login to the existing user
            sociallogin.connect(request, user)
        except:
            print('failed to get the user and connect them at social login')
