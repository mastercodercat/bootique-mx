from django.test import TestCase
from mock import patch, Mock

from common.decorators import *


class MockRequest(object):
    pass


def prepare_mock_request():
    request = MockRequest()
    request.user = None
    return request


class CommonInspectionDecoratorsTestCase(TestCase):

    @patch('common.decorators.can_read_inspection', return_value=True)
    def test_inspection_readable_required_allow(self, mock_decr_can_read_inspection):
        func = Mock(return_value='allowed')
        decorated_func = inspection_readable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response, 'allowed')

    @patch('common.decorators.can_read_inspection', return_value=False)
    def test_inspection_readable_required_disallow(self, mock_decr_can_read_inspection):
        func = Mock(return_value='allowed')
        decorated_func = inspection_readable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response.status_code, 403)

    @patch('common.decorators.can_write_inspection', return_value=True)
    def test_inspection_writable_required_allow(self, mock_decr_can_write_inspection):
        func = Mock(return_value='allowed')
        decorated_func = inspection_writable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response, 'allowed')

    @patch('common.decorators.can_write_inspection', return_value=False)
    def test_inspection_writable_required_disallow(self, mock_decr_can_write_inspection):
        func = Mock(return_value='allowed')
        decorated_func = inspection_writable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response.status_code, 403)


class CommonGanttDecoratorsTestCase(TestCase):

    @patch('common.decorators.can_read_gantt', return_value=True)
    def test_gantt_readable_required_allow(self, mock_decr_can_read_gantt):
        func = Mock(return_value='allowed')
        decorated_func = gantt_readable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response, 'allowed')

    @patch('common.decorators.can_read_gantt', return_value=False)
    def test_gantt_readable_required_disallow(self, mock_decr_can_read_gantt):
        func = Mock(return_value='allowed')
        decorated_func = gantt_readable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response.status_code, 403)

    @patch('common.decorators.can_write_gantt', return_value=True)
    def test_gantt_writable_required_allow(self, mock_decr_can_write_gantt):
        func = Mock(return_value='allowed')
        decorated_func = gantt_writable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response, 'allowed')

    @patch('common.decorators.can_write_gantt', return_value=False)
    def test_gantt_writable_required_disallow(self, mock_decr_can_write_gantt):
        func = Mock(return_value='allowed')
        decorated_func = gantt_writable_required(func)
        request = prepare_mock_request()
        response = decorated_func(request)
        self.assertEqual(response.status_code, 403)
