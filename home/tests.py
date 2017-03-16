from django.test import TestCase
from home.models import *


class AircraftTestCase(TestCase):
    fixtures = ['aircraft', 'inspection', 'aircraft_inspection_record']

    def test_aircraft_inspections(self):
        a1 = Aircraft.objects.get(pk=1)
        a2 = Aircraft.objects.get(pk=2)
        self.assertIsNot(len(a1.inspections), 0)
        self.assertIs(len(a2.inspections), 0)

    def test_aircraft_next_due_inspection(self):
        a1 = Aircraft.objects.get(pk=1)
        a2 = Aircraft.objects.get(pk=2)
        self.assertIsNot(a1.next_inspection_due, None)
        self.assertIs(a2.next_inspection_due, None)
