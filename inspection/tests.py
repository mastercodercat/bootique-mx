from django.test import TestCase
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from inspection.models import *
from home.models import *


class ViewsTestCase(TestCase):
    fixtures = ['roles', 'inspection']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')
        user_role = UserRole.objects.get(name='Admin')
        self.user_profile = UserProfile(is_admin=False, personal_data=None, user=self.user, role=user_role)
        self.user_profile.save()

    def force_login(self):
        user_role = UserRole.objects.get(name='Admin')
        self.user_profile.role = user_role
        self.user_profile.save()
        self.client.login(username=self.user.username, password='tester_password')

    def logout(self):
        self.client.logout()

    def guest_attempt(self, url):
        login_url = reverse('account_login')

        self.logout()
        response = self.client.get(url)
        self.assertRedirects(response, login_url + '?next=' + url)

    def no_role_user_attempt(self, url):
        self.user_profile.role = None
        self.user_profile.save()
        self.client.login(username=self.user.username, password='tester_password')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def authorized_attempt(self, url, template):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def url_not_found_attempt(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_view_index(self):
        view_url = reverse('inspection:index')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'index.html')

    def test_view_inspection_program_details(self):
        view_url = reverse('inspection:inspection_program_details', kwargs={
            'program_id': 1
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'program.html')
        self.url_not_found_attempt(reverse('inspection:inspection_program_details', kwargs={
            'program_id': 10    # invalid program_id in fixture
        }))

    def test_view_create_inspection_program(self):
        view_url = reverse('inspection:create_inspection_program')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'create_program.html')

        response = self.client.post(view_url, {
            'name': 'Test Program',
            'inspection_tasks': (1, 2, 3),
        })
        self.assertRedirects(response, reverse('inspection:index'))

    def test_view_add_inspection_task(self):
        view_url = reverse('inspection:add_inspection_task', kwargs={
            'program_id': 1,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'add_task.html')
        self.url_not_found_attempt(reverse('inspection:add_inspection_task', kwargs={
            'program_id': 10    # invalid program_id in fixture
        }))

        program = InspectionProgram.objects.get(pk=1)
        program.inspection_tasks.remove(InspectionTask.objects.get(pk=1))
        response = self.client.post(view_url, {
            'inspection_task': 1,
        })
        self.assertRedirects(response, reverse('inspection:inspection_program_details', kwargs={
            'program_id': 1,
        }))

