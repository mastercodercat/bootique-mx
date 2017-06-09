from django.test import TestCase
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import json

from routeplanning.models import *
from home.models import *
from common.helpers import *


class UnitTestCase(TestCase):
    fixtures = ['tails', 'assignments_test', 'flights_test']

    def test_assignment_is_valid_method(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 13, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 14, 30, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 0, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 24, 19, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 20, 10, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 25, 12, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 14, 30, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 24, 14, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2)
        self.assertIs(result, False)

        assignment_to_exclude_check = Assignment.objects.get(pk=451)
        d1 = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        result = Assignment.is_duplicated(tail, d1, d2, assignment_to_exclude_check)
        self.assertIs(result, False)

    def test_assignment_is_physically_valid_method(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        result = Assignment.is_physically_valid(tail, 'MCE', 'OAK', d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        result = Assignment.is_physically_valid(tail, 'LAX', 'OAK', d1, d2)
        self.assertIs(result, False)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        result = Assignment.is_physically_valid(tail, 'MCE', 'ATL', d1, d2)
        self.assertIs(result, False)

        d1 = datetime(2017, 5, 24, 23, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 0, 10, tzinfo=utc)
        result = Assignment.is_physically_valid(tail, 'MCE', 'OAK', d1, d2)
        self.assertIs(result, True)

        d1 = datetime(2017, 5, 24, 23, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 0, 10, tzinfo=utc)
        result = Assignment.is_physically_valid(tail, 'MCE', 'LAX', d1, d2)
        self.assertIs(result, False)

        assignment_to_move = Assignment.objects.select_related('flight').get(pk=455)
        d1 = datetime(2017, 5, 25, 13, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 14, 45, tzinfo=utc)
        result = Assignment.is_physically_valid(
            tail,
            assignment_to_move.flight.origin,
            assignment_to_move.flight.destination,
            d1,
            d2,
            assignment_to_move
        )
        self.assertIs(result, True)

class ViewsTestCase(TestCase):
    fixtures = ['roles', 'lines', 'lineparts', 'tails', 'assignments_test', 'flights_test']

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
        view_url = reverse('routeplanning:index')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'gantt.html')
        self.authorized_attempt(view_url + '?mode=1', 'gantt.html')
        self.authorized_attempt(view_url + '?mode=2', 'gantt.html')
        self.authorized_attempt(view_url + '?mode=3&start=1494799200', 'gantt.html')
        self.authorized_attempt(view_url + '?mode=4', 'gantt.html')
        self.authorized_attempt(view_url + '?mode=5&end=1496008800', 'gantt.html')
        self.authorized_attempt(view_url + '?mode=6&end=1496008800', 'gantt.html')

    def test_view_add_tail(self):
        view_url = reverse('routeplanning:add_tail')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'tail.html')

        response = self.client.post(view_url, {
            'number': 'N990XX',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))
        self.assertNotEqual(Tail.objects.filter(number='N990XX').count(), 0)

        response = self.client.post(view_url, {
            'number': 'N991XX',
            'action_after_save': 'save-and-add-another',
        })
        self.assertTemplateUsed(response, 'tail.html')
        self.assertNotEqual(Tail.objects.filter(number='N991XX').count(), 0)

        response = self.client.post(view_url, {
            'number': 'N992XX',
            'action_after_save': 'save-and-continue',
        })
        tail = Tail.objects.get(number='N992XX')
        self.assertRedirects(response, reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        }))

    def test_view_edit_tail(self):
        tail = Tail(number='N992XX')
        tail.save()
        view_url = reverse('routeplanning:edit_tail', kwargs={
            'tail_id': tail.id,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'tail.html')

        response = self.client.post(view_url, {
            'number': 'N993XX',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))

        response = self.client.post(view_url, {
            'number': 'N993XX',
            'action_after_save': 'save-and-add-another',
        })
        self.assertRedirects(response, reverse('routeplanning:add_tail'))

        response = self.client.post(view_url, {
            'number': 'N993XX',
            'action_after_save': 'save-and-continue',
        })
        self.assertTemplateUsed(response, 'tail.html')

    def test_view_delete_tail(self):
        tail = Tail(number='N992XX')
        tail.save()
        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': tail.id,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()

        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)

        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': 999,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Error occurred while deleting tail')

        view_url = reverse('routeplanning:delete_tail', kwargs={
            'tail_id': 0,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Error occurred while deleting tail')

        response = self.client.post(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Only DELETE method allowed for this api')

    def test_view_coming_due(self):
        tail = Tail.objects.first()
        view_url = reverse('routeplanning:coming_due', kwargs={
            'tail_id': tail.id,
            'revision_id': 0,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'comingdue.html')

    def test_view_add_line(self):
        view_url = reverse('routeplanning:add_line')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'line.html')

        response = self.client.post(view_url, {
            'name': 'XXX/YYY',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))
        self.assertNotEqual(Line.objects.filter(name='XXX/YYY').count(), 0)

        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-add-another',
        })
        self.assertTemplateUsed(response, 'line.html')
        self.assertNotEqual(Line.objects.filter(name='XXX/ZZZ').count(), 0)

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

    def test_view_edit_line(self):
        line = Line(name='XXX/YYY')
        line.save()
        view_url = reverse('routeplanning:edit_line', kwargs={
            'line_id': line.id,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'line.html')

        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save',
        })
        self.assertRedirects(response, reverse('routeplanning:index'))

        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-add-another',
        })
        self.assertRedirects(response, reverse('routeplanning:add_line'))

        response = self.client.post(view_url, {
            'name': 'XXX/ZZZ',
            'part1': '701',
            'part2': '702',
            'action_after_save': 'save-and-continue',
        })
        self.assertTemplateUsed(response, 'line.html')

    def test_view_delete_line(self):
        line = Line(name='XXX/YYY')
        line.save()
        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': line.id,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()

        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)

        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': 999,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Error occurred while deleting line')

        view_url = reverse('routeplanning:delete_line', kwargs={
            'line_id': 0,
        })
        response = self.client.delete(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Error occurred while deleting line')

        response = self.client.post(view_url)
        data = json.loads(response.content)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 'Only DELETE method allowed for this api')

    def test_view_flights(self):
        view_url = reverse('routeplanning:flights')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'flights.html')

    def test_view_add_flight(self):
        view_url = reverse('routeplanning:add_flight')

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'flight.html')

        response = self.client.post(view_url, {
            'number': '801',
            'origin': 'MCE',
            'destination': 'LAX',
            'departure_datetime': '2017-05-15 10:00:00',
            'arrival_datetime': '2017-05-15 12:00:00',
            'type': 1,
        })
        flight = Flight.objects.get(number='801')
        self.assertRedirects(response, reverse('routeplanning:edit_flight', kwargs={
            'flight_id': flight.id
        }))
        self.assertNotEqual(Flight.objects.filter(number='801').count(), 0)

    def test_view_edit_flight(self):
        view_url = reverse('routeplanning:edit_flight', kwargs={
            'flight_id': 13069,
        })

        self.guest_attempt(view_url)
        self.no_role_user_attempt(view_url)
        self.force_login()
        self.authorized_attempt(view_url, 'flight.html')

        response = self.client.post(view_url, {
            'number': '801',
            'origin': 'XXX',
            'destination': 'YYY',
            'departure_datetime': '2017-05-15 10:00:00',
            'arrival_datetime': '2017-05-15 12:00:00',
            'type': 1,
        })
        self.assertTemplateUsed(response, 'flight.html')
        self.assertNotEqual(Flight.objects.filter(number='801').count(), 0)

    def test_view_delete_flight(self):
        view_url = reverse('routeplanning:delete_flights')

        self.force_login()

        response = self.client.post(view_url, {
            'flight_ids': '13069, 13070'
        })
        self.assertRedirects(response, reverse('routeplanning:flights'))

    def test_api_get_flight_page(self):
        api_url = reverse('routeplanning:api_flight_get_page')

        self.force_login()

        response = self.client.post(api_url, {
            'start': 0,
            'length': 10,
            'order[0][dir]': 'asc',
            'order[0][column]': 1,
            'search[value]': 'MCE',
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['data']), 0)

    def test_api_load_data(self):
        api_url = reverse('routeplanning:api_load_data')

        self.force_login()

        response = self.client.get(api_url, {
            'startdate': 1494799200,
            'enddate': 1496008800,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(len(data['assignments']), 0)
        self.assertNotEqual(len(data['templates']), 0)

    def test_api_assign_flight(self):
        api_url = reverse('routeplanning:api_assign_flight')

        self.force_login()

        Assignment.objects.all().delete()

        response = self.client.post(api_url, {
            'flight_data': json.dumps([{
                'flight': 13069,
                'tail': 'N455BC',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(data['success'], True)
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
        self.assertEqual(data['success'], True)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

    def test_api_assign_status(self):
        api_url = reverse('routeplanning:api_assign_status')

        self.force_login()

        response = self.client.post(api_url, {
            'tail': 'N455BC',
            'start_time': '2017-05-24 17:30:00+00',
            'end_time': '2017-05-24 18:00:00+00',
            'status': 2,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

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
        self.assertEqual(data['success'], True)

        response = self.client.post(api_url, {
            'tail': 'N584JV',
            'start_time': '2017-05-24 17:50:00+00',
            'end_time': '2017-05-24 18:50:00+00',
            'status': 2,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)

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
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)

    def test_api_remove_assignment(self):
        api_url = reverse('routeplanning:api_remove_assignment')

        self.force_login()

        response = self.client.post(api_url, {
            'assignment_data': '[450, 451]',
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_api_move_assignment(self):
        api_url = reverse('routeplanning:api_move_assignment')

        self.force_login()

        Assignment.objects.exclude(pk=455).exclude(pk=451).delete()

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
        self.assertEqual(data['success'], True)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], False)

        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 451,
                'tail': 'N584JV',
                'start_time': '2017-05-25T12:30:00Z',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['duplication'], True)
        self.assertEqual(data['physically_invalid'], False)

        assignment = Assignment.objects.get(pk=451)
        assignment.flight.origin = 'OAK'
        assignment.flight.save()
        response = self.client.post(api_url, {
            'assignment_data': json.dumps([{
                'assignment_id': 451,
                'tail': 'N584JV',
                'start_time': '2017-05-26T12:30:00Z',
            }]),
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['duplication'], False)
        self.assertEqual(data['physically_invalid'], True)

    def test_api_resize_assignment(self):
        api_url = reverse('routeplanning:api_resize_assignment')

        self.force_login()

        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': 600,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'end',
            'diff_seconds': 600,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        response = self.client.post(api_url, {
            'assignment_id': 451,
            'position': 'start',
            'diff_seconds': 18000,
            'revision': 0,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], False)

    def test_api_save_hobbs(self):
        api_url = reverse('routeplanning:api_save_hobbs')

        self.force_login()

        response = self.client.post(api_url, {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_api_get_hobbs(self):
        self.force_login()

        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })

        hobbs = Hobbs.objects.first()

        api_url = reverse('routeplanning:api_get_hobbs', kwargs={
            'hobbs_id': hobbs.id,
        })

        response = self.client.get(api_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_api_delete_actual_hobbs(self):
        self.force_login()

        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })

        hobbs = Hobbs.objects.first()

        api_url = reverse('routeplanning:api_delete_actual_hobbs', kwargs={
            'hobbs_id': hobbs.id,
        })

        response = self.client.post(api_url)
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_api_coming_due_list(self):
        self.force_login()

        r = self.client.post(reverse('routeplanning:api_save_hobbs'), {
            'tail_id': 14,
            'type': Hobbs.TYPE_ACTUAL,
            'hobbs': 10,
            'datetime': '2017-05-24T13:00:00Z',
            'flight_id': 13072,
        })

        api_url = reverse('routeplanning:api_coming_due_list')

        response = self.client.post(api_url, {
            'tail_id': 14,
            'start': '2017-05-23T10:00:00Z',
            'days': 7,
        })
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertNotEqual(len(data['hobbs_list']), 0)

