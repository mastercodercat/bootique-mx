import json
from mock import patch
from django.test import TestCase
from datetime import datetime
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from routeplanning.models import *
from home.models import *
from common.helpers import *


class TailTestCase(TestCase):
    fixtures = ['tails', 'assignments_test', 'flights_test']

    def test_get_last_assignment(self):
        tail = Tail.objects.get(pk=14)
        last_assignment = tail.get_last_assignment(None, '2017-06-01T00:00:00Z')
        self.assertEqual(last_assignment.id, 456)

    def test_get_last_assignment_with_time_period_criteria(self):
        tail = Tail.objects.get(pk=14)
        last_assignment = tail.get_last_assignment(None, '2017-05-25T00:00:00Z')
        self.assertEqual(last_assignment.id, 457)

    def test_get_last_assignment_none(self):
        tail = Tail.objects.get(pk=15)
        last_assignment = tail.get_last_assignment(None, '2017-06-01T00:00:00Z')
        self.assertIsNone(last_assignment)

    def test_get_last_assignment_on_revision(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.filter(pk__in=[450, 451, 457]).update(revision=revision)

        tail = Tail.objects.get(pk=14)
        last_assignment = tail.get_last_assignment(revision, '2017-05-24T20:30:00Z')
        self.assertEqual(last_assignment.id, 451)


class LineTestCase(TestCase):
    fixtures = ['lines', 'flights_test']

    def setUp(self):
        line = Line.objects.get(pk=1)
        line_part1 = LinePart(number='322', line=line)
        line_part1.save()

    def test_flights_property(self):
        line = Line.objects.get(pk=1)
        flight_ids = [flight.id for flight in line.flights]
        self.assertEqual(set(flight_ids), set([13069, 13072]))


class FlightTestCase(TestCase):
    fixtures = ['tails', 'assignments_test', 'flights_test']

    def test_update_flight_estimates(self):
        flight = Flight.objects.get(pk=13069)
        flight.estimated_out_datetime = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        flight.update_flight_estimates_and_actuals()
        self.assertEqual(
            flight.estimated_in_datetime,
            datetime(2017, 5, 24, 16, 15, tzinfo=utc)
        )

    def test_update_flight_actuals(self):
        flight = Flight.objects.get(pk=13069)
        flight.actual_out_datetime = datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        flight.update_flight_estimates_and_actuals()
        self.assertEqual(
            flight.actual_in_datetime,
            datetime(2017, 5, 24, 17, 15, tzinfo=utc)
        )

    def test_update_assignment_actuals_on_flight_estimated(self):
        flight = Flight.objects.get(pk=13069)
        flight.estimated_out_datetime = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        flight.update_assignment_datetimes()
        assignment = flight.assignment_set.first()
        self.assertEqual(
            assignment.start_time,
            datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        )
        self.assertEqual(
            assignment.end_time,
            datetime(2017, 5, 24, 16, 15, tzinfo=utc)
        )

    def test_update_assignment_actuals_on_flight_actual(self):
        flight = Flight.objects.get(pk=13069)
        flight.actual_out_datetime = datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        flight.update_assignment_datetimes()
        assignment = flight.assignment_set.first()
        self.assertEqual(
            assignment.start_time,
            datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        )
        self.assertEqual(
            assignment.end_time,
            datetime(2017, 5, 24, 17, 15, tzinfo=utc)
        )


class AssignmentTestCase(TestCase):
    fixtures = ['tails', 'assignments_test', 'flights_test']

    def test_length_property(self):
        assignment = Assignment.objects.first()
        length_time_delta = assignment.end_time - assignment.start_time
        self.assertEqual(
            assignment.length,
            length_time_delta.total_seconds(),
        )

    def test_get_revision_assignments(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        assignment_ids = [450, 451, 453]
        Assignment.objects.filter(pk__in=assignment_ids).update(revision=revision)
        revision_assignments = Assignment.get_revision_assignments(revision)
        ra_ids = [assignment.id for assignment in revision_assignments]
        self.assertEqual(
            set(ra_ids),
            set(assignment_ids)
        )

    def test_get_revision_assignments_on_draft(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        assignment_ids = [450, 451]
        Assignment.objects.filter(pk__in=assignment_ids).update(revision=revision)
        revision.check_draft_created()

        revision_assignments = Assignment.get_revision_assignments(revision)
        ra_ids = [assignment.id for assignment in revision_assignments]
        self.assertEqual(
            set(ra_ids),
            set(assignment_ids)
        )

    def test_get_revision_assignments_all(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        assignment_ids = [450, 451, 453]
        Assignment.objects.filter(pk__in=assignment_ids).update(revision=revision)
        Assignment.objects.filter(pk__in=[450, 451]).update(is_draft=True)

        revision_assignments = Assignment.get_revision_assignments_all(revision)
        ra_ids = [assignment.id for assignment in revision_assignments]
        self.assertEqual(
            set(ra_ids),
            set(assignment_ids)
        )

    def test_duplication_check_conflict_on_start_time(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 13, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 14, 30, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2)
        self.assertIsNot(result, None)
        self.assertEqual(result.id, 450)

    def test_duplication_check_conflict_on_end_time(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 14, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 15, 30, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2)
        self.assertIsNot(result, None)
        self.assertEqual(result.id, 451)

    def test_duplication_check_conflict_inside_another(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 19, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 20, 10, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2)
        self.assertIsNot(result, None)
        self.assertEqual(result.id, 454)

    def test_duplication_check_conflict_overlap_another(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 25, 12, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 14, 30, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2)
        self.assertIsNot(result, None)
        self.assertEqual(result.id, 455)

    def test_duplication_check_no_conflict(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 14, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2)
        self.assertIs(result, None)

    def test_duplication_check_no_conflict_with_exclude_option(self):
        tail = Tail.objects.get(pk=14)

        assignment_to_exclude_check = Assignment.objects.get(pk=451)
        d1 = datetime(2017, 5, 24, 15, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 16, 0, tzinfo=utc)
        result = Assignment.duplication_check(None, tail, d1, d2, assignment_to_exclude_check)
        self.assertIs(result, None)

    def test_physical_conflict_no_conflict(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(None, tail, 'MCE', 'OAK', d1, d2)
        self.assertIs(conflict, None)

    def test_physical_conflict_origin_conflict_for_new_assignment(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(None, tail, 'LAX', 'OAK', d1, d2)
        self.assertEqual(conflict['direction'], 'destination')

    def test_physical_conflict_destination_conflict_for_new_assignment(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 16, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 24, 17, 30, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(None, tail, 'MCE', 'ATL', d1, d2)
        self.assertEqual(conflict['direction'], 'origin')

    def test_physical_conflict_no_conflict_2(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 23, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 0, 10, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(None, tail, 'MCE', 'OAK', d1, d2)
        self.assertIs(conflict, None)

    def test_physical_conflict_destination_conflict_for_new_assignment_2(self):
        tail = Tail.objects.get(pk=14)

        d1 = datetime(2017, 5, 24, 23, 0, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 0, 10, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(None, tail, 'MCE', 'LAX', d1, d2)
        self.assertEqual(conflict['direction'], 'origin')

    def test_physical_conflict_no_conflict_with_exclude_option(self):
        tail = Tail.objects.get(pk=14)

        assignment_to_exclude_check = Assignment.objects.select_related('flight').get(pk=455)
        d1 = datetime(2017, 5, 25, 13, 30, tzinfo=utc)
        d2 = datetime(2017, 5, 25, 14, 45, tzinfo=utc)
        conflict = Assignment.physical_conflict_check(
            None,
            tail,
            assignment_to_exclude_check.flight.origin,
            assignment_to_exclude_check.flight.destination,
            d1,
            d2,
            assignment_to_exclude_check
        )
        self.assertIs(conflict, None)

    def test_get_duplicated_assignments(self):
        tail = Tail.objects.get(pk=14)

        dup_assignments = Assignment.get_duplicated_assignments(None, tail, '2017-05-24T13:30:00Z', '2017-05-24T18:00:00Z')
        da_ids = [assignment.id for assignment in dup_assignments]
        self.assertEqual(
            set(da_ids),
            set([450, 451, 453])
        )

    def test_get_duplicated_assignments_with_exclude_option(self):
        tail = Tail.objects.get(pk=14)

        assignment_to_exclude_check = Assignment.objects.get(pk=451)
        dup_assignments = Assignment.get_duplicated_assignments(
            None, tail, '2017-05-24T13:30:00Z', '2017-05-24T18:00:00Z', assignment_to_exclude_check
        )
        da_ids = [assignment.id for assignment in dup_assignments]
        self.assertEqual(
            set(da_ids),
            set([450, 453])
        )

    def test_get_duplicated_assignments_with_exclude_option_on_revision(self):
        tail = Tail.objects.get(pk=14)

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.filter(pk__in=[450, 451, 453, 457]).update(revision=revision)

        assignment_to_exclude_check = Assignment.objects.get(pk=451)
        dup_assignments = Assignment.get_duplicated_assignments(
            revision, tail, '2017-05-24T13:30:00Z', '2017-05-24T18:00:00Z', assignment_to_exclude_check
        )
        da_ids = [assignment.id for assignment in dup_assignments]
        self.assertEqual(
            set(da_ids),
            set([450, 453])
        )

    def test_apply_revision(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        assignment = Assignment.objects.first()
        assignment.apply_revision(revision)
        self.assertEqual(assignment.is_draft, False)
        self.assertEqual(assignment.revision, revision)

    def test_apply_revision_draft(self):
        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc), has_draft=True)
        revision.save()
        assignment = Assignment.objects.first()
        assignment.apply_revision(revision)
        self.assertEqual(assignment.is_draft, True)
        self.assertEqual(assignment.revision, revision)


class RevisionTestCase(TestCase):
    fixtures = ['tails', 'assignments_test', 'flights_test']

    def setUp(self):
        self.revision1 = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        self.revision1.save()
        self.revision2 = Revision(published_datetime=datetime(2017, 7, 05, 0, 0, tzinfo=utc))
        self.revision2.save()
        Assignment.objects.filter(pk__lte=454).update(revision=self.revision1)
        Assignment.objects.filter(pk__gte=455).update(revision=self.revision2)

    def test_get_latest_revision(self):
        revision = Revision.get_latest_revision()
        self.assertEqual(revision, self.revision1)

    def test_create_draft(self):
        Revision.create_draft()
        draft_assignments = Assignment.objects.filter(is_draft=True).filter(revision=None).select_related('flight')
        da_flight_ids = [assignment.flight.id for assignment in draft_assignments]
        da_flight_numbers = [assignment.flight.number for assignment in draft_assignments]
        self.assertEqual(
            set(da_flight_ids),
            set([13069, 13070, 13185, 13262])
        )
        self.assertEqual(
            set(da_flight_numbers),
            set(['322', '326', '0', '0'])
        )

    def test_check_draft_created(self):
        self.revision1.check_draft_created()
        self.assertEqual(self.revision1.has_draft, True)

        revision_assignments_original = Assignment.objects.filter(revision=self.revision1).filter(is_draft=False)
        rao_ids = set([assignment.id for assignment in revision_assignments_original])
        revision_assignments_draft = Assignment.objects.filter(revision=self.revision1).filter(is_draft=True)
        rad_ids = set([assignment.id for assignment in revision_assignments_draft])
        self.assertEqual(rad_ids, set([450, 451, 453, 454]))
        self.assertEqual(len(rao_ids), 4)
        self.assertEqual(len(rao_ids.intersection(rad_ids)), 0)


class HobbsTestCase(TestCase):
    fixtures = ['tails', 'hobbs_test', 'assignments_test', 'flights_test']

    def test_get_hobbs(self):
        tail = Tail.objects.get(pk=14)
        hobbs_qset = Hobbs.get_hobbs(tail, '2017-05-24T00:00:00Z', '2017-05-26T00:00:00Z')
        hobbs_ids = [hobbs.id for hobbs in hobbs_qset]
        self.assertEqual(set(hobbs_ids), set([1, 2, 3, 4, 5]))

    def test_get_last_actual_hobbs(self):
        tail = Tail.objects.get(pk=14)
        last_actual_hobbs = Hobbs.get_last_actual_hobbs(tail, '2017-05-25T00:00:00Z')
        self.assertEqual(last_actual_hobbs.id, 4)

    def test_get_last_actual_hobbs_returns_none(self):
        tail = Tail.objects.get(pk=14)
        last_actual_hobbs = Hobbs.get_last_actual_hobbs(tail, '2017-05-23T00:00:00Z')
        self.assertIsNone(last_actual_hobbs)

    def test_get_projected_value_before_assignments_for_draft_revision(self):
        tail = Tail.objects.get(pk=14)
        Assignment.objects.update(is_draft=True)

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-23T00:00:00Z', None)
        self.assertEqual(projected_hobbs, 0)

    def test_get_projected_value_at_middle_of_assignments_for_draft_revision(self):
        tail = Tail.objects.get(pk=14)
        Assignment.objects.update(is_draft=True)

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-24T18:00:00Z', None)
        self.assertEqual(round(projected_hobbs, 2), round(90 + 1.25 + 0.67, 2))

    def test_get_projected_value_before_assignments_for_revision_with_draft(self):
        tail = Tail.objects.get(pk=14)

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.update(revision=revision)
        revision.check_draft_created()

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-23T00:00:00Z', revision)
        self.assertEqual(projected_hobbs, 0)

    def test_get_projected_value_at_middle_of_assignments_for_revision_with_draft(self):
        tail = Tail.objects.get(pk=14)

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.update(revision=revision)
        revision.check_draft_created()

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-24T18:00:00Z', revision)
        self.assertEqual(round(projected_hobbs, 2), round(90 + 1.25 + 0.67, 2))

    def test_get_projected_value_before_assignments_for_revision_without_draft(self):
        tail = Tail.objects.get(pk=14)

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.update(revision=revision)

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-23T00:00:00Z', revision)
        self.assertEqual(projected_hobbs, 0)

    def test_get_projected_value_at_middle_of_assignments_for_revision_without_draft(self):
        tail = Tail.objects.get(pk=14)

        revision = Revision(published_datetime=datetime(2017, 7, 10, 0, 0, tzinfo=utc))
        revision.save()
        Assignment.objects.update(revision=revision)

        projected_hobbs = Hobbs.get_projected_value(tail, '2017-05-24T18:00:00Z', revision)
        self.assertEqual(round(projected_hobbs, 2), round(90 + 1.25 + 0.67, 2))

    def test_get_next_due(self):
        tail = Tail.objects.get(pk=14)
        next_due_hobbs = Hobbs.get_next_due(tail, '2017-05-24T12:00:00Z')
        self.assertEqual(next_due_hobbs.id, 1)

    def test_get_next_due_value(self):
        tail = Tail.objects.get(pk=14)
        next_due_hobbs_value = Hobbs.get_next_due_value(tail, '2017-05-24T12:00:00Z')
        self.assertEqual(next_due_hobbs_value, 95)
