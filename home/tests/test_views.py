import json
from mock import patch
from django.test import TestCase
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from rest_framework.test import APIClient

from home.models import *


class ViewsTestCase(TestCase):
    fixtures = ['roles', 'inspection', 'aircraft', 'airframes', 'engines', 'propellers', 'lines', 'lineparts', 'tails']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')
        self.client.login(username=self.user.username, password='tester_password')
        self.aircraft = Aircraft.objects.get(pk=1)
        self.api_client = APIClient()

    def no_role_user_attempt(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def authorized_attempt(self, url, template):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def url_not_found_attempt(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_view_overview_no_permission_fail(self, mock_decr_can_read_inspection):
        view_url = reverse('home:overview')
        self.no_role_user_attempt(view_url)

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_overview_authorized_success(self, mock_decr_can_read_inspection):
        view_url = reverse('home:overview')
        self.authorized_attempt(view_url, 'overview.html')

    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_view_aircraft_details_no_permission_fail(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_details', kwargs={
            'reg': self.aircraft.reg
        })
        self.no_role_user_attempt(view_url)

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_details_authorized_success(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_details', kwargs={
            'reg': self.aircraft.reg
        })
        self.authorized_attempt(view_url, 'details.html')

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_details_url_not_found_fail(self, mock_decr_can_read_inspection):
        self.url_not_found_attempt(reverse('home:aircraft_details', kwargs={
            'reg': 'someinvalidvalue'
        }))

    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_view_aircraft_task_list_no_permission_fail(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        })
        self.no_role_user_attempt(view_url)

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_task_list_authorized_success(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        })
        self.authorized_attempt(view_url, 'task_list.html')

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_task_list_url_not_found_fail(self, mock_decr_can_read_inspection):
        self.url_not_found_attempt(reverse('home:aircraft_task_list', kwargs={
            'reg': 'someinvalidvalue'
        }))

    ###
    # This view should be tested before aircraft_task because it assigns self.aircraft to an inspection program for testing
    ###
    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_view_aircraft_assign_program_no_permission_fail(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_assign', kwargs={
            'reg': self.aircraft.reg
        })
        self.no_role_user_attempt(view_url)

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_assign_program_authorized_success(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_assign', kwargs={
            'reg': self.aircraft.reg
        })
        self.authorized_attempt(view_url, 'assign_inspection_program.html')

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_assign_program_url_not_found_fail(self, mock_decr_can_read_inspection):
        self.url_not_found_attempt(reverse('home:aircraft_assign', kwargs={
            'reg': 'someinvalidvalue'
        }))

    @patch('common.decorators.can_read_inspection', return_value=True)
    @patch('home.views.can_write_inspection', return_value=True)
    def test_view_aircraft_assign_program_save(
        self, mock_decr_can_read_inspection, mock_can_write_inspection
    ):
        inspection_component = InspectionComponent(
            name='Test Component',
            inspection_task=InspectionTask.objects.get(pk=16),
            pn='20-10',
            sn=''
        )
        inspection_component.save()

        view_url = reverse('home:aircraft_assign', kwargs={
            'reg': self.aircraft.reg
        })
        response = self.client.post(view_url, {
            'inspection_program': 1,
        })
        self.assertRedirects(response, reverse('home:aircraft_task_list', kwargs={
            'reg': self.aircraft.reg
        }))

    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_view_aircraft_task_no_permission_fail(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })
        self.no_role_user_attempt(view_url)

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_task_authorized_success(self, mock_decr_can_read_inspection):
        view_url = reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })
        self.authorized_attempt(view_url, 'task.html')

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_task_url_not_found_fail_invalid_aircraft_reg(
        self, mock_decr_can_read_inspection
    ):
        view_url = reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })
        self.url_not_found_attempt(reverse('home:aircraft_task', kwargs={
            'reg': 'someinvalidvalue',
            'task_id': 17,
        }))

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_view_aircraft_task_url_not_found_fail_invalid_task_id(
        self, mock_decr_can_read_inspection
    ):
        view_url = reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })
        self.url_not_found_attempt(reverse('home:aircraft_task', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 999,
        }))

    def test_api_aircraft_task_list_get(self):
        self.api_client.force_authenticate(self.user)

        api_url = reverse('home:api_aircraft_task_list', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })

        response = self.api_client.get(api_url, {})
        data = json.loads(response.content)
        self.assertNotEqual(data['task']['id'], 0)
        self.assertNotEqual(len(data['components']), 0)

    @patch('common.decorators.can_read_inspection', return_value=True)
    @patch('home.views.can_write_inspection', return_value=True)
    def test_api_aircraft_task_list_post(self, mock_can_write_inspection, mock_decr_can_read_inspection):
        self.api_client.force_authenticate(self.user)

        api_url = reverse('home:api_aircraft_task_list', kwargs={
            'reg': self.aircraft.reg,
            'task_id': 17,
        })

        # assign program to aircraft
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
