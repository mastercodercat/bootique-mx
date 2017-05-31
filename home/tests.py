from django.test import TestCase
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient
import json

from home.models import *


class ViewsTestCase(TestCase):
    fixtures = ['roles', 'inspection', 'aircraft', 'airframes', 'engines', 'propellers', 'lines', 'lineparts', 'tails']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')
        user_role = UserRole.objects.get(name='Admin')
        self.user_profile = UserProfile(is_admin=False, personal_data=None, user=self.user, role=user_role)
        self.user_profile.save()
        self.aircraft = Aircraft.objects.get(pk=1)
        self.api_client = APIClient()

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

    def test_view_overview(self):
        view_url = reverse('home:overview')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'overview.html')

    def test_view_aircraft_details(self):
        view_url = reverse('home:aircraft_details', kwargs={
            'reg': self.aircraft.reg
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'details.html')
        self.url_not_found_attempt(reverse('home:aircraft_details', kwargs={
            'reg': 'someinvalidvalue'
        }))

    def test_view_aircraft_task_list(self):
        view_url = reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'task_list.html')
        self.url_not_found_attempt(reverse('home:aircraft_task_list', kwargs={
            'reg': 'someinvalidvalue'
        }))

    ###
    # This view should be tested before aircraft_task because it assigns self.aircraft to an inspection program for testing
    ###
    def test_view_aircraft_assign_program(self):
        view_url = reverse('home:aircraft_assign', kwargs={
            'reg': self.aircraft.reg
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'assign_inspection_program.html')
        self.url_not_found_attempt(reverse('home:aircraft_assign', kwargs={
            'reg': 'someinvalidvalue'
        }))

        inspection_component = InspectionComponent(
            name='Test Component',
            inspection_task=InspectionTask.objects.get(pk=16),
            pn='20-10',
            sn=''
        )
        inspection_component.save()

        response = self.client.post(view_url, {
            'inspection_program': 1,
        })
        self.assertRedirects(response, reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        }))

    def test_view_aircraft_task(self):
        view_url = reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'task.html')
        self.url_not_found_attempt(reverse('home:aircraft_task', kwargs={
            'reg': 'someinvalidvalue',
            'task_id': 17,
        }))
        self.url_not_found_attempt(reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 999,
        }))

    def test_api_aircraft_task_list(self):
        api_url = reverse('home:api_aircraft_task_list', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })

        response = self.api_client.get(api_url, {})
        self.assertEqual(response.status_code, 403)
        self.api_client.force_authenticate(self.user)

        response = self.api_client.get(api_url, {})
        data = json.loads(response.content)
        self.assertNotEqual(data['task']['id'], 0)
        self.assertNotEqual(len(data['components']), 0)

        # assign program to aircraft
        self.force_login()
        response = self.client.post(reverse('home:aircraft_assign', kwargs={
            'reg': self.aircraft.reg
        }), {
            'inspection_program': 1,
        })
        self.assertRedirects(response, reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        }))

        existing_ic_sub_item = InspectionComponentSubItem.objects.filter(
            aircraft=self.aircraft,
            inspection_component_id=1
        ).first()

        # case of successful field update
        response = self.api_client.post(api_url, {
            'component_id': 1,
            'sub_item_id': existing_ic_sub_item.id,
            'field': 'interval',
            'value': 100,
        })
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], True)
        self.assertEqual(response.status_code, 200)

        # case of invalid component id
        response = self.api_client.post(api_url, {
            'component_id': 99,
            'sub_item_id': existing_ic_sub_item.id,
            'field': 'interval',
            'value': 100,
        })
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response.status_code, 200)

        # case of invalid component sub item id
        response = self.api_client.post(api_url, {
            'component_id': 1,
            'sub_item_id': 99,
            'field': 'interval',
            'value': 100,
        })
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response.status_code, 200)

        # case of invalid field name
        response = self.api_client.post(api_url, {
            'component_id': 1,
            'sub_item_id': existing_ic_sub_item.id,
            'field': 'nonexistingfield',
            'value': 100,
        })
        response_data = json.loads(response.content)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response.status_code, 200)

