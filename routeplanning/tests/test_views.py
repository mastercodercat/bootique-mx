import json
from mock import patch
from django.test import TestCase
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from routeplanning.models import *
from home.models import *
from common.helpers import *


class RoutePlanningViewsTestCase(TestCase):
    fixtures = ['roles', 'lines', 'lineparts', 'tails', 'assignments_test', 'flights_test']

    def setUp(self):
        self.user = User.objects.create_user(username='tester', email='tester@tester.com', password='tester_password')
        self.client.login(username=self.user.username, password='tester_password')

    def no_role_user_attempt_test(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def authorized_attempt_test(self, url, template):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template)

    def prepare_revision(self):
        Assignment.objects.update(is_draft=True)

        response = self.client.post(reverse('routeplanning:api_publish_revision'), {
            'revision': '0',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 1)

        return Revision.objects.first()

    @patch('routeplanning.permissions.can_read_gantt', return_value=False)
    def test_view_index_no_permission_fail(self, mock):
        self.no_role_user_attempt_test(reverse('routeplanning:index'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_index_authorized_success(self, mock):
        view_url = reverse('routeplanning:index')
        self.authorized_attempt_test(view_url, 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=1', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=2', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=3&start=1494799200', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=4', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=5&end=1496008800', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=6&end=1496008800', 'gantt.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_index_context_when_session_saved_states(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session['mode'] = '2'
        session.save()

        view_url = reverse('routeplanning:index')
        response = self.client.get(view_url)
        self.assertEqual(response.context['start_tmstmp'], 1503071850)
        self.assertEqual(response.context['mode'], '2')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_index_context_when_session_saved_states_and_url_params_exist(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session['mode'] = '2'
        session.save()

        view_url = reverse('routeplanning:index')
        response = self.client.get(view_url + '?mode=3&start=1503071851')
        self.assertEqual(response.context['start_tmstmp'], 1503071851)
        self.assertEqual(response.context['mode'], '3')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_index_context_when_session_saved_states_and_end_tmstmp_exist(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session.save()

        view_url = reverse('routeplanning:index')
        response = self.client.get(view_url + '?end=1503071900')
        self.assertEqual(response.context['start_tmstmp'], 1503071900 - 14 * 24 * 3600)

    @patch('routeplanning.permissions.can_read_gantt', return_value=False)
    def test_view_current_published_gantt_no_permission_fail(self, mock):
        view_url = reverse('routeplanning:view_current_published_gantt')
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_current_published_gantt_authorized_success(self, mock):
        view_url = reverse('routeplanning:view_current_published_gantt')
        self.authorized_attempt_test(view_url, 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=1', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=2', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=3&start=1494799200', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=4', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=5&end=1496008800', 'gantt.html')
        self.authorized_attempt_test(view_url + '?mode=6&end=1496008800', 'gantt.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_current_published_gantt_context_when_session_saved_states(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session['mode'] = '2'
        session.save()

        view_url = reverse('routeplanning:view_current_published_gantt')
        response = self.client.get(view_url)
        self.assertEqual(response.context['start_tmstmp'], 1503071850)
        self.assertEqual(response.context['mode'], '2')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_current_published_gantt_context_when_session_saved_states_and_url_params_exist(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session['mode'] = '2'
        session.save()

        view_url = reverse('routeplanning:view_current_published_gantt')
        response = self.client.get(view_url + '?mode=3&start=1503071851')
        self.assertEqual(response.context['start_tmstmp'], 1503071851)
        self.assertEqual(response.context['mode'], '3')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_current_published_gantt_context_when_session_saved_states_and_end_tmstmp_exist(self, mock):
        session = self.client.session
        session['start_tmstmp'] = 1503071850
        session.save()

        view_url = reverse('routeplanning:view_current_published_gantt')
        response = self.client.get(view_url + '?end=1503071900')
        self.assertEqual(response.context['start_tmstmp'], 1503071900 - 14 * 24 * 3600)

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_add_tail_no_permission_fail(self, mock):
        view_url = reverse('routeplanning:add_tail')
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_tail_authorized_success(self, mock):
        view_url = reverse('routeplanning:add_tail')
        self.authorized_attempt_test(view_url, 'tail.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_tail_save(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_tail')
        response = self.client.post(view_url, {
            'number': 'N990XX',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))
        self.assertNotEqual(Tail.objects.filter(number='N990XX').count(), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_tail_save_and_add_another(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_tail')
        response = self.client.post(view_url, {
            'number': 'N991XX',
            'action_after_save': 'save-and-add-another',
        })
        self.assertNotEqual(Tail.objects.filter(number='N991XX').count(), 0)
        self.assertRedirects(response, reverse('routeplanning:add_tail'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_tail_save_and_continue(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_tail')
        response = self.client.post(view_url, {
            'number': 'N992XX',
            'action_after_save': 'save-and-continue',
        })
        tail = Tail.objects.get(number='N992XX')
        self.assertRedirects(response, reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        }))

    @patch('routeplanning.permissions.can_read_gantt', return_value=False)
    def test_view_edit_tail_no_permission_fail(self, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_tail_authorized_success(self, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        self.authorized_attempt_test(view_url, 'tail.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_edit_tail_save_no_permission_fail(self, mock_can_write_gantt, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.post(view_url, {
            'number': 'N455BC',
            'action_after_save': 'save',
        })
        self.assertEqual(response.status_code, 403)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_tail_save(self, mock_can_write_gantt, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.post(view_url, {
            'number': 'N455BC',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_tail_save_and_add_another(self, mock_can_write_gantt, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.post(view_url, {
            'number': 'N455BC',
            'action_after_save': 'save-and-add-another',
        })
        self.assertRedirects(response, reverse('routeplanning:add_tail'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_tail_save_and_continue(self, mock_can_write_gantt, mock_can_read_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.post(view_url, {
            'number': 'N455BC',
            'action_after_save': 'save-and-continue',
        })
        self.assertRedirects(response, view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_delete_tail_no_permission_fail(self, mock_can_write_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 403)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_tail_delete_success(self, mock_can_write_gantt):
        tail = Tail.objects.get(number='N455BC')
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 204)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_tail_delete_fail_invalid_id(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': 999,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Error occurred while deleting tail')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_tail_delete_fail_id_0(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': 0,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Error occurred while deleting tail')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_tail_delete_fail_invalid_method(self, mock_can_write_gantt):
        tail = Tail.objects.first()
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': tail.id,
        })
        response = self.client.post(view_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 405)

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_coming_due_no_permission_fail(self, mock_can_write_gantt):
        tail = Tail.objects.first()
        view_url = reverse('routeplanning:coming_due', kwargs={
            'tail_id': tail.id,
            'revision_id': 0,
        })
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_coming_due_authorized_success(self, mock_can_write_gantt):
        tail = Tail.objects.first()
        view_url = reverse('routeplanning:coming_due', kwargs={
            'tail_id': tail.id,
            'revision_id': 0,
        })
        self.authorized_attempt_test(view_url, 'comingdue.html')

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_add_line_no_permission_fail(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:add_line')
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_line_authorized_success(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:add_line')
        self.authorized_attempt_test(view_url, 'line.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_line_save(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_line')
        response = self.client.post(view_url, {
            'name': 'XXX/YYY',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))
        self.assertNotEqual(Line.objects.filter(name='XXX/YYY').count(), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_line_save(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_line')
        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-add-another',
        })
        self.assertTemplateUsed(response, 'line.html')
        self.assertNotEqual(Line.objects.filter(name='XXX/ZZZ').count(), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_line_save(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:add_line')
        response = self.client.post(view_url, {
            'name': 'YYY/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-continue',
        })
        line = Line.objects.get(name='YYY/ZZZ')
        self.assertRedirects(response, reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        }))

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_edit_line_no_permission_fail(self, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_line_authorized_success(self, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        self.authorized_attempt_test(view_url, 'line.html')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_edit_line_save_no_permission_fail(self, mock_view_can_write_gantt, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save',
        })
        self.assertEqual(response.status_code, 403)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_line_save(self, mock_view_can_write_gantt, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_line_save_and_add_another(self, mock_can_write_gantt, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-add-another',
        })
        self.assertRedirects(response, reverse('routeplanning:add_line'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_line_save_and_continue(self, mock_view_can_write_gantt, mock_can_read_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-continue',
        })
        self.assertRedirects(response, view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_delete_line_no_permission_fail(self, mock_can_write_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 403)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_line_success(self, mock_can_write_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 204)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_line_fail_invalid_id(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': 999,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Error occurred while deleting line')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_line_fail_invalid_id_0(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': 0,
        })
        response = self.client.delete(view_url)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Error occurred while deleting line')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_line_fail_invalid_method(self, mock_can_write_gantt):
        line = Line.objects.get(name='LAX/MCE')
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': line.id,
        })
        response = self.client.post(view_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 405)

    @patch('routeplanning.permissions.can_read_gantt', return_value=False)
    def test_view_flights_no_permission_fail(self, mock_can_read_gantt):
        view_url = reverse('routeplanning:flights')
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_view_flights_authorized_success(self, mock_can_read_gantt):
        view_url = reverse('routeplanning:flights')
        self.authorized_attempt_test(view_url, 'flights.html')

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_add_flight_no_permission_fail(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:add_flight')
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_flight_authorized_success(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:add_flight')
        self.authorized_attempt_test(view_url, 'flight.html')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_add_flight_save(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:add_flight')
        response = self.client.post(view_url, {
            'number': '801',
            'origin': 'MCE',
            'destination': 'LAX',
            'scheduled_out_datetime': '2017-05-15 10:00:00',
            'scheduled_in_datetime': '2017-05-15 12:00:00',
            'type': 1,
        })
        flight = Flight.objects.get(number='801')
        self.assertRedirects(response, reverse('routeplanning:edit_flight', kwargs={
            'flight_id': flight.id
        }))
        self.assertNotEqual(Flight.objects.filter(number='801').count(), 0)

    @patch('routeplanning.permissions.can_write_gantt', return_value=False)
    def test_view_edit_flight_no_permission_fail(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:edit_flight', kwargs={
            'flight_id': 13069,
        })
        self.no_role_user_attempt_test(view_url)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_flight_authorized_success(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:edit_flight', kwargs={
            'flight_id': 13069,
        })
        self.authorized_attempt_test(view_url, 'flight.html')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_edit_flight_save(self, mock_can_write_gantt):
        view_url = reverse('routeplanning:edit_flight', kwargs={
            'flight_id': 13069,
        })
        response = self.client.post(view_url, {
            'number': '801',
            'origin': 'XXX',
            'destination': 'YYY',
            'scheduled_out_datetime': '2017-05-15 10:00:00',
            'scheduled_in_datetime': '2017-05-15 12:00:00',
            'type': 1,
        })
        self.assertNotEqual(Flight.objects.filter(number='801').count(), 0)
        self.assertRedirects(response, view_url)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_view_delete_flights(self, mock_can_write_gantt, mock_can_read_gantt):
        view_url = reverse('routeplanning:delete_flights')
        flight_ids = ['14001', '14002']
        response = self.client.post(view_url, {
            'flight_ids': ', '.join(flight_ids)
        })
        self.assertEqual(Flight.objects.filter(pk__in=flight_ids).count(), 0)
        self.assertRedirects(response, reverse('routeplanning:flights'))

    @patch('routeplanning.permissions.can_read_gantt', return_value=False)
    def test_api_get_flight_page_no_permission_fail(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_flight_get_page')
        response = self.client.get(api_url, {
            'start': 0,
            'length': 10,
            'order[0][dir]': 'asc',
            'order[0][column]': 1,
            'search[value]': 'MCE',
        })
        self.assertEqual(response.status_code, 403)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_get_flight_page_success(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_flight_get_page')
        response = self.client.get(api_url, {
            'start': 0,
            'length': 10,
            'order[0][dir]': 'asc',
            'order[0][column]': 1,
            'search[value]': 'MCE',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data['data']), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_get_flight_page_success_order_desc(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_flight_get_page')
        response = self.client.get(api_url, {
            'start': 0,
            'length': 10,
            'order[0][dir]': 'desc',
            'order[0][column]': 1,
            'search[value]': 'MCE',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data['data']), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.views.api_views.can_write_gantt', return_value=False)
    def test_api_load_data_fail_on_draft(self, mock_can_write_gantt, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_load_data')
        response = self.client.get(api_url, {
            'startdate': 1494799200,
            'enddate': 1496008800,
            'revision': 0,
        });
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], 'Not allowed to get draft route plan')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.views.api_views.can_write_gantt', return_value=False)
    def test_api_load_data_fail_on_non_latest_revision(self, mock_can_write_gantt, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_load_data')

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        revision1 = Revision(published_datetime=datetime(2017, 7, 05, 0, 0, tzinfo=utc))
        revision1.save()

        response = self.client.get(api_url, {
            'startdate': 1494799200,
            'enddate': 1496008800,
            'revision': revision1.id,
        });
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], 'Not allowed to get route plans other than current published version')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.views.api_views.can_write_gantt', return_value=True)
    def test_api_load_data_fail_no_revision(self, mock_can_write_gantt, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_load_data')
        response = self.client.get(api_url, {
            'startdate': 1494799200,
            'enddate': 1496008800,
            'revision': 999,
        });
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.views.api_views.can_write_gantt', return_value=True)
    def test_api_load_data_success_on_draft(self, mock_can_write_gantt, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_load_data')
        response = self.client.get(api_url, {
            'startdate': 1495648800,
            'enddate': 1496008800,
            'revision': 0,
        });
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data['assignments']), 0)
        self.assertNotEqual(len(data['templates']), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.views.api_views.can_write_gantt', return_value=True)
    def test_api_load_data_success_on_revision(self, mock_can_write_gantt, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_load_data')

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        revision1 = Revision(published_datetime=datetime(2017, 7, 05, 0, 0, tzinfo=utc))
        revision1.save()

        response = self.client.get(api_url, {
            'startdate': 1495648800,
            'enddate': 1496008800,
            'revision': revision1.id,
        });
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_flight_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_flight')
        response = self.client.post(api_url, {
            'flight_data': 'invalid_json_string',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['flight_data'], [u'Value must be valid JSON.'])

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_flight_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_flight')
        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13069,
                'tail': 'N455BC',
            }]),
            'revision': 1,
        })
        data = json.loads(response.content)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_flight_successes_and_failures(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_flight')

        Assignment.objects.all().delete()

        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13069,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13072,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['physically_invalid'], True)

        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13262,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 14001,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], True)

        # Testing estimated and actual flight times
        flight = Flight.objects.get(pk=13070)
        flight.estimated_out_datetime = datetime(2017, 5, 24, 19, 30, tzinfo=utc)
        flight.update_flight_estimates_and_actuals()
        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13070,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        flight = Flight.objects.get(pk=13263)
        flight.estimated_out_datetime = datetime(2017, 5, 24, 21, 50, tzinfo=utc)
        flight.actual_out_datetime = datetime(2017, 5, 24, 22, 0, tzinfo=utc)
        flight.update_flight_estimates_and_actuals()
        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13263,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        # Testing with existing revision
        revision = self.prepare_revision()
        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13072,
                'tail': 'N455BC',
            }]),
            'revision': revision.id,
        })
        data = json.loads(response.content)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_status_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_status')
        response = self.client.post(api_url, {
            'tail': 'N455BC',
            'start_time': '2017-05-24 17:30:00+00',
            'end_time': '2017-05-24 18:00:00+00',
            'status': 'n',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn('status', data)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_status_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_status')
        response = self.client.post(api_url, {
            'tail': 'N455BC',
            'start_time': '2017-05-24 17:30:00+00',
            'end_time': '2017-05-24 18:00:00+00',
            'status': 2,
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_assign_status_successes_and_failures(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_assign_status')
        response = self.client.post(api_url, {
            'tail': 'N455BC',
            'start_time': '2017-05-24 17:30:00+00',
            'end_time': '2017-05-24 18:00:00+00',
            'status': 2,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        Assignment.objects.exclude(pk=450).delete()

        response = self.client.post(api_url, {
            'tail': 'N584JV',
            'start_time': '2017-05-24 18:30:00+00',
            'end_time': '2017-05-24 19:30:00+00',
            'status': 3,
            'origin': 'LAX',
            'destination': 'MCE',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(api_url, {
            'tail': 'N584JV',
            'start_time': '2017-05-24 17:50:00+00',
            'end_time': '2017-05-24 18:50:00+00',
            'status': 2,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Duplicated assignment')

        response = self.client.post(api_url, {
            'tail': 'N584JV',
            'start_time': '2017-05-24 20:00:00+00',
            'end_time': '2017-05-24 21:30:00+00',
            'status': 3,
            'origin': 'LAX',
            'destination': 'OAK',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Physically invalid assignment')

        response = self.client.post(api_url, {
            'tail': 'N999XX',   # invalid tail number which will lead to error
            'start_time': '2017-05-24 17:50:00+00',
            'end_time': '2017-05-24 18:50:00+00',
            'status': 2,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)

        # Testing with existing revision
        revision = self.prepare_revision()
        response = self.client.post(api_url, {
            'tail': 'N584JV',
            'start_time': '2017-05-25 17:50:00+00',
            'end_time': '2017-05-25 18:50:00+00',
            'status': 2,
            'revision': revision.id,
        })
        self.assertEqual(response.status_code, 200)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_remove_assignment_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_remove_assignment')
        response = self.client.post(api_url, {
            'assignment_data': 'invalid_json_data',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn('assignment_data', data)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_remove_assignment_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_remove_assignment')
        response = self.client.post(api_url, {
            'assignment_data': '[450, 451]',
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_remove_assignment_success(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_remove_assignment')
        response = self.client.post(api_url, {
            'assignment_data': '[450, 451, 999]',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        left_assignment_count = Assignment.objects.filter(pk__in=[450, 451, 999]).count()
        self.assertEqual(left_assignment_count, 0)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_move_assignment_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_move_assignment')
        response = self.client.post(api_url, {
            'assignment_data': 'invalid_json_data',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertIn('assignment_data', data)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_move_assignment_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_move_assignment')
        response = self.client.post(api_url, {
            'assignment_data': '[]',
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_move_assignment_successes_and_failures(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_move_assignment')
        Assignment.objects.exclude(pk=450).exclude(pk=451).exclude(pk=455).delete()
        Assignment.objects.all().update(is_draft=True)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 455,
                'tail': 'N165TG',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 455,
                'tail': 'N166TG',
                'start_time': 'invalid_date_string',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 451,
                'tail': 'N584JV',
                'start_time': '2017-05-25T11:00:00Z',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 450,
                'tail': 'N166TG',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['physically_invalid'], True)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 451,
                'tail': 'N166TG',
                'start_time': '2017-05-25T13:30:00Z',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['duplication'], True)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_resize_assignment_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_resize_assignment')
        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': 'not-a-number',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid parameters')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_resize_assignment_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_resize_assignment')
        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': 600,
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_resize_assignment_fail_start_time_bigger_than_end_time(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_resize_assignment')
        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': -12000,   # start_time would get bigger than end_time which should be detected as error
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Start time cannot be later than end time')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_resize_assignment_fail_invalid_assignment_id(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_resize_assignment')
        response = self.client.post(api_url, {
            'assignment_id': 999,
            'position': 'start',
            'diff_seconds': 600,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid assignment ID')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_resize_assignment_successes_and_failures(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_resize_assignment')
        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': 600,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'end',
            'diff_seconds': 600,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        # Prepare an assignment for simulating time overlap
        Assignment.objects.filter(pk=453).update(is_draft=True)
        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'end',
            'diff_seconds': 180000,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Duplicated assignment')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_save_hobbs_fail_invalid_parameters(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_save_hobbs')
        response = self.client.post(api_url, {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': 'invalid_date_string',
            'flight_id': 13072,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid parameters')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_save_hobbs_successes_and_failures(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_save_hobbs')
        response = self.client.post(api_url, {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

        hobbs = Hobbs.objects.first()

        response = self.client.post(api_url, {
            'tail_id': 14,
            'id': hobbs.id,
            'type': Hobbs.TYPE_NEXT_DUE,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid parameters')

        response = self.client.post(api_url, {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': hobbs.id,
            'hobbs': 8,
            'datetime': '2017-05-25T05:00:00Z',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_get_hobbs(self, mock_can_write_gantt, mock_can_read_gantt):
        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })

        hobbs = Hobbs.objects.first()

        api_url = reverse('routeplanning:api_hobbs', kwargs={
            'hobbs_id': hobbs.id,
        })
        response = self.client.get(api_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_delete_actual_hobbs(self, mock_can_write_gantt):
        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })
        hobbs = Hobbs.objects.first()

        api_url = reverse('routeplanning:api_hobbs', kwargs={
            'hobbs_id': hobbs.id,
        })
        response = self.client.delete(api_url)
        self.assertEqual(response.status_code, 204)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_coming_due_list_fail_invalid_parameters(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_coming_due_list')
        response = self.client.post(api_url, {
            'tail_id': 14,
            'start': 'invalid_date_string',
            'days': 7,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Invalid parameters')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_coming_due_list_fail_no_revision(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_coming_due_list')
        response = self.client.post(api_url, {
            'tail_id': 14,
            'start': '2017-05-23T10:00:00Z',
            'days': 7,
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_coming_due_list_success(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_coming_due_list')
        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })

        response = self.client.post(api_url, {
            'tail_id': 14,
            'start': '2017-05-23T10:00:00Z',
            'days': 7,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data['hobbs_list']), 0)

    @patch('routeplanning.permissions.can_read_gantt', return_value=True)
    def test_api_coming_due_list_success_on_revision(self, mock_can_read_gantt):
        api_url = reverse('routeplanning:api_coming_due_list')
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        response = self.client.post(api_url, {
            'tail_id': 14,
            'start': '2017-05-23T10:00:00Z',
            'days': 7,
            'revision': revision.id,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_publish_revision_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_publish_revision')
        response = self.client.post(api_url, {
            'revision': 999,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_publish_revision_successes(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_publish_revision')

        Assignment.objects.update(is_draft=True)

        response = self.client.post(api_url, {
            # 'revision': '0',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 1)

        revision = Revision.objects.first()
        self.assertNotEqual(revision.assignment_set.count(), 0)

        response = self.client.post(api_url, {
            'revision': revision.id,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 2)

        revision.check_draft_created()

        response = self.client.post(api_url, {
            'revision': revision.id,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 3)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_clear_revision_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_clear_revision')
        response = self.client.post(api_url, {
            'revision': '999',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_clear_revision_successes(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_clear_revision')

        Assignment.objects.update(is_draft=True)

        response = self.client.post(reverse('routeplanning:api_publish_revision'), {
            # 'revision': '0',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 1)

        revision = Revision.objects.first()

        response = self.client.post(api_url, {
            'revision': revision.id,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(revision.assignment_set.filter(is_draft=True).count(), 0)

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_delete_revision_fail_no_revision(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_delete_revision')
        response = self.client.post(api_url, {
            'revision': '999',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['error'], 'Revision not found')

    @patch('routeplanning.permissions.can_write_gantt', return_value=True)
    def test_api_delete_revision_successes(self, mock_can_write_gantt):
        api_url = reverse('routeplanning:api_delete_revision')

        Assignment.objects.update(is_draft=True)
        revision_to_remove = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision_to_remove.save()

        response = self.client.post(reverse('routeplanning:api_publish_revision'), {
            # 'revision': '0',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 2)

        response = self.client.post(api_url, {
            'revision': revision_to_remove.id,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['revisions']), 1)
