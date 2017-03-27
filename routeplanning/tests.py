from django.test import TestCase

from django.test import TestCase
from routeplanning.models import *


class FlightTestCase(TestCase):
    fixtures = ['tails', 'lines', 'flights']

    def test_flight_is_available_on_weekday(self):
        f1 = Flight.objects.get(pk=1)
        self.assertIs(f1.is_available_on_weekday(0), True)
        self.assertIs(f1.is_available_on_weekday(4), True)
        self.assertIs(f1.is_available_on_weekday(5), False)
        self.assertIs(f1.is_available_on_weekday(6), False)

    def test_flight_is_available_on_weekday_period(self):
        f1 = Flight.objects.get(pk=1)
        self.assertIs(f1.is_available_on_weekday_period(0, 6), True)
        self.assertIs(f1.is_available_on_weekday_period(4, 5), True)
        self.assertIs(f1.is_available_on_weekday_period(5, 6), False)
        self.assertIs(f1.is_available_on_weekday_period(6, 0), True)
        self.assertIs(f1.is_available_on_weekday_period(6, 5), True)

        f2 = Flight.objects.get(pk=2)
        self.assertIs(f2.is_available_on_weekday_period(0, 6), True)
        self.assertIs(f2.is_available_on_weekday_period(6, 0), False)
