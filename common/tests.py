from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from home.models import *


class ViewsTestCase(TestCase):
    fixtures = ['roles', 'inspection', 'aircraft', 'airframes', 'engines', 'propellers', 'lines', 'lineparts', 'tails']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')

    def force_login(self):
        self.client.login(username=self.user.username, password='tester_password')

    def logout(self):
        self.client.logout()

    def test_view_index_redirect(self):
        view_url = reverse('index_redirect')

        # Maintenance user redirect to Maintenance dashboard
        user_role = UserRole.objects.get(name='Maintenance')
        user_profile = UserProfile(is_admin=False, personal_data=None, user=self.user, role=user_role)
        user_profile.save()
        self.force_login()
        ### aircraft home redirect test disabled for now
        # response = self.client.get(view_url)
        # self.assertRedirects(response, reverse('home:overview'))

        # Dispatcher user redirect to gantt dashboard
        user_role = UserRole.objects.get(name='Dispatcher')
        user_profile.role = user_role
        user_profile.save()
        response = self.client.get(view_url)
        self.assertRedirects(response, reverse('routeplanning:view_current_published_gantt'))

        # User without role will see no-permissions page
        user_profile.role = None
        user_profile.save()
        response = self.client.get(view_url)
        self.assertTemplateUsed(response, 'no-permissions.html')

        # Guest users will see sign in page
        self.logout()
        response = self.client.get(view_url)
        self.assertRedirects(response, reverse('account_login'))

