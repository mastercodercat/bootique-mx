from django.test import TestCase
from routeplanning.models import *
from common.helpers import *
from datetime import datetime


class RouteplanningTestCase(TestCase):
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
