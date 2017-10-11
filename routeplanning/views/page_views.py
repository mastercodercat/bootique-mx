from datetime import timedelta, datetime
import json
import dateutil.parser
import random
import os
import csv

from django.conf import settings
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, ProtectedError, Max
from django.http import HttpResponse, HttpResponseForbidden
from django.middleware import csrf
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from rest_framework.permissions import IsAuthenticated

from common.helpers import *
from common.views.generic import TemplateView
from common.views.generic import FormView
from common.views.generic import CreateView
from common.views.generic import UpdateView
from routeplanning.models import *
from routeplanning.forms import *
from routeplanning.permissions import GanttReadPermission
from routeplanning.permissions import GanttWritePermission


class GanttPageView(TemplateView):
    permission_classes = (IsAuthenticated, GanttReadPermission)

    def get_context_data(self, **kwargs):
        context = super(GanttPageView, self).get_context_data(**kwargs)

        request = self.request
        read_only = self.is_read_only()

        if request.GET.get('mode'):
            mode = request.GET.get('mode')
        elif 'mode' in request.session:
            mode = request.session['mode']
        else:
            mode = '4'

        start_tmstmp = int(request.GET.get('start', 0))
        end_tmstmp = int(request.GET.get('end', 0))
        if not(start_tmstmp or end_tmstmp):
            start_tmstmp = request.session['start_tmstmp'] \
                if 'start_tmstmp' in request.session \
                else None

        tails = Tail.objects.all()
        lines = Line.objects.order_by('name').all()

        days_options = {'1': 1, '2': 1, '3': 1, '4': 1, '5': 3, '6': 7}          # Date mark count
        hours_options = {'1': 3, '2': 6, '3': 12, '4': 24, '5': 24, '6': 6}      # Hours mark count
        units_per_hour_options = {'1': 4, '2': 2, '3': 1, '4': 1, '5': 1, '6': 0.25}

        days = days_options[mode]

        hours = hours_options[mode]
        units_per_hour = units_per_hour_options[mode]

        if not start_tmstmp:
            if end_tmstmp:
                start_tmstmp = int(end_tmstmp) - 14 * 24 * 3600
            else:
                start_time = datetime_now_utc()
                start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
                start_tmstmp = totimestamp(start_time)

        big_unit_colspan = units_per_hour * hours if units_per_hour > 1 else hours
        big_unit_count = 14 * (24 / hours) if days == 1 else 14
        table_length_in_secs = 14 * 24 * 3600

        context.update({
            'tails': tails,
            'lines': lines,
            'big_units': big_unit_count,
            'small_units': big_unit_colspan * big_unit_count,
            'days': days,
            'hours': hours,
            'big_unit_colspan': big_unit_colspan,
            'units_per_hour': units_per_hour,
            'mode': mode,
            'start_tmstmp': start_tmstmp,
            'end_tmstmp': end_tmstmp,
            'start_param_exists': 'true' if request.GET.get('start') or 'start_tmstmp' in request.session else 'false',
            'end_param_exists': 'true' if request.GET.get('end') else 'false',
            'prev_start_tmstmp': int(start_tmstmp) - table_length_in_secs,
            'next_start_tmstmp': int(start_tmstmp) + table_length_in_secs,
            'csrf_token': csrf.get_token(request),
            'window_at_end': request.GET.get('window_at_end') or 0,
            'revisions': Revision.objects.order_by('-published_datetime'),
            'read_only': read_only,
        })
        self.context_data = context

        return context

    def update_session(self):
        self.request.session['mode'] = self.context_data['mode']
        self.request.session['start_tmstmp'] = self.context_data['start_tmstmp']

    def is_read_only(self):
        return False

    def get(self, *args, **kwargs):
        response = super(GanttPageView, self).get(*args, **kwargs)
        self.update_session()
        return response


class IndexView(GanttPageView):
    template_name = 'gantt.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['page'] = 'routeplanning:index'
        return context

    def is_read_only(self):
        return not can_write_gantt(self.request.user)


class CurrentPublishedGanttView(GanttPageView):
    template_name = 'gantt.html'

    def get_context_data(self, **kwargs):
        context = super(CurrentPublishedGanttView, self).get_context_data(**kwargs)
        context['page'] = 'routeplanning:view_current_published_gantt'
        return context

    def is_read_only(self):
        return True


class AddTailView(CreateView):
    template_name = 'tail.html'
    form_class = TailForm
    model = Tail
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_context_data(self, **kwargs):
        context = super(AddTailView, self).get_context_data(**kwargs)
        tails = Tail.objects.all()
        context.update({
            'title': 'Add Tail',
            'tails': tails,
        })
        return context

    def get_success_url(self):
        action_after_save = self.request.POST.get('action_after_save')
        if action_after_save == 'save-and-continue':
            return reverse('routeplanning:edit_tail', kwargs={
                'tail_id': self.object.id
            })
        elif action_after_save == 'save':
            return reverse('routeplanning:index')
        else:
            return reverse('routeplanning:add_tail')


class EditTailView(UpdateView):
    template_name = 'tail.html'
    form_class = TailForm
    model = Tail
    permission_classes = (IsAuthenticated, GanttWritePermission)
    pk_url_kwarg = 'tail_id'

    def get_context_data(self, **kwargs):
        context = super(EditTailView, self).get_context_data(**kwargs)
        tails = Tail.objects.all()
        tail = self.object
        context.update({
            'title': 'Edit Tail ' + tail.number,
            'tails': tails,
        })
        return context

    def get_success_url(self):
        action_after_save = self.request.POST.get('action_after_save')
        if action_after_save == 'save-and-continue':
            return reverse('routeplanning:edit_tail', kwargs={
                'tail_id': self.object.id
            })
        elif action_after_save == 'save':
            return reverse('routeplanning:index')
        else:
            return reverse('routeplanning:add_tail')


class ComingDueView(TemplateView):
    template_name = 'comingdue.html'
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_context_data(self, tail_id=None, revision_id=None, **kwargs):
        tail = Tail.objects.get(pk=tail_id)
        context = {
            'tail': tail,
            'tails': [],
            'revision_id': revision_id if revision_id else 0,
        }
        return context


class AddLineView(FormView):
    template_name = 'line.html'
    form_class = LineForm
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_context_data(self, **kwargs):
        context = super(AddLineView, self).get_context_data(**kwargs)
        lines = Line.objects.all()
        context.update({
            'title': 'Add Line',
            'lines': lines,
        })
        return context

    def get_success_url(self):
        action_after_save = self.request.POST.get('action_after_save')
        if action_after_save == 'save-and-continue':
            return reverse('routeplanning:edit_line', kwargs={
                'line_id': self.object.id
            })
        elif action_after_save == 'save':
            return reverse('routeplanning:index')
        else:
            return reverse('routeplanning:add_line')

    def form_valid(self, form):
        line = Line(name=form.cleaned_data['name'])
        line.save()
        self.object = line
        for i in range(1, 12):
            entered_line_part_number = form.cleaned_data['part' + str(i)]
            if entered_line_part_number:
                line_part = LinePart(number=entered_line_part_number, line=line)
                line_part.save()
            else:
                break
        return super(AddLineView, self).form_valid(form)


class EditLineView(FormView):
    template_name = 'line.html'
    form_class = LineForm
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_context_data(self, **kwargs):
        context = super(EditLineView, self).get_context_data(**kwargs)
        lines = Line.objects.all()
        line = self.object
        context.update({
            'title': 'Edit Line ' + line.name,
            'lines': lines,
        })
        return context

    def get_success_url(self):
        action_after_save = self.request.POST.get('action_after_save')
        if action_after_save == 'save-and-continue':
            return reverse('routeplanning:edit_line', kwargs={
                'line_id': self.object.id
            })
        elif action_after_save == 'save':
            return reverse('routeplanning:index')
        else:
            return reverse('routeplanning:add_line')

    def get_initial(self):
        initial_data = super(EditLineView, self).get_initial()
        line = self.object
        initial_data.update({
            'name': line.name,
        })
        for i, line_part in enumerate(line.linepart_set.all()):
            initial_data['part' + str(i + 1)] = line_part.number
        return initial_data

    def form_valid(self, form):
        line = self.object
        if line.name != form.cleaned_data['name']:
            line.name = form.cleaned_data['name']
            line.save()

        line.linepart_set.all().delete()
        for i in range(1, 12):
            entered_line_part_number = form.cleaned_data['part' + str(i)]
            if entered_line_part_number:
                line_part = LinePart(number=entered_line_part_number, line=line)
                line_part.save()
            else:
                break
        return super(EditLineView, self).form_valid(form)

    def get(self, *args, **kwargs):
        line_id = kwargs.get('line_id')
        self.object = get_object_or_404(Line, pk=line_id)
        return super(EditLineView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        line_id = kwargs.get('line_id')
        self.object = get_object_or_404(Line, pk=line_id)
        return super(EditLineView, self).post(*args, **kwargs)


class FlightListView(TemplateView):
    template_name = 'flights.html'
    permission_classes = (IsAuthenticated, GanttReadPermission)

    def get_context_data(self, **kwargs):
        context = super(FlightListView, self).get_context_data(**kwargs)
        context['flights'] = []
        return context


class AddFlightView(CreateView):
    template_name = 'flight.html'
    form_class = FlightForm
    model = Flight
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_context_data(self, **kwargs):
        context = super(AddFlightView, self).get_context_data(**kwargs)
        context.update({
            'title': 'Add Flight',
        })
        return context

    def get_success_url(self):
        return reverse('routeplanning:edit_flight', kwargs={
            'flight_id': self.object.id
        })


class EditFlightView(UpdateView):
    template_name = 'flight.html'
    form_class = FlightForm
    model = Flight
    permission_classes = (IsAuthenticated, GanttWritePermission)
    pk_url_kwarg = 'flight_id'

    def get_context_data(self, **kwargs):
        context = super(EditFlightView, self).get_context_data(**kwargs)
        context.update({
            'title': 'Edit Flight',
        })
        return context

    def get_success_url(self):
        return reverse('routeplanning:edit_flight', kwargs={
            'flight_id': self.object.id
        })

    def form_valid(self, form):
        response = super(EditFlightView, self).form_valid(form)
        self.object.update_assignment_datetimes()
        return response


class DeleteFlightView(FormView):
    form_class = DeleteMultipleFlightsForm
    permission_classes = (IsAuthenticated, GanttWritePermission)

    def get_success_url(self):
        return reverse('routeplanning:flights')

    def form_valid(self, form):
        ids_string = form.cleaned_data['flight_ids']
        ids = ids_string.split(',')
        for id in ids:
            try:
                Flight.objects.filter(pk=id).delete()
            except ProtectedError:
                pass
        return super(DeleteFlightView, self).form_valid(form)
