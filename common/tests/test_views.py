from django.test import TestCase
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from mock import patch


class IndexRedirectViewTestCase(TestCase):

    def force_login(self):
        self.client.login(username=self.user.username, password='tester_password')

    def logout(self):
        self.client.logout()

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')
        self.force_login()

    # @patch('common.views.can_read_gantt', return_value=False)
    # @patch('common.views.can_read_inspection', return_value=True)
    # @patch('common.decorators.can_read_inspection', return_value=True)
    # def test_redirect_maintenance_user_to_aircraft_dashboard(
    #     self, mock_decr_can_read_inspection, mock_can_read_inspection, mock_can_read_gantt
    # ):
    #     """
    #     Maintenance user redirect to Maintenance dashboard
    #     """
    #     view_url = reverse('index_redirect')
    #     response = self.client.get(view_url)
    #     self.assertRedirects(response, reverse('home:overview'))

    @patch('common.views.can_read_gantt', return_value=True)
    @patch('common.decorators.can_read_gantt', return_value=True)
    def test_redirect_dispatcher_user_to_gantt_dashboard(
        self, mock_decr_can_read_gantt, mock_can_read_gantt
    ):
        """
        Dispatcher user redirect to current published gantt view
        """
        view_url = reverse('index_redirect')
        response = self.client.get(view_url)
        self.assertRedirects(response, reverse('routeplanning:view_current_published_gantt'))

    @patch('common.views.can_read_gantt', return_value=False)
    @patch('common.views.can_read_inspection', return_value=False)
    def test_redirect_no_role_user_to_no_permissions_page(self, mock_can_read_inspection, mock_can_read_gantt):
        """
        User without role will see no-permissions page
        """
        view_url = reverse('index_redirect')
        response = self.client.get(view_url)
        self.assertTemplateUsed(response, 'home-empty.html')

    def test_redirect_guest_user_to_login_page(self):
        """
        Guest users will see sign in page
        """
        self.logout()
        view_url = reverse('index_redirect')
        response = self.client.get(view_url)
        self.assertRedirects(response, reverse('account_login'))

