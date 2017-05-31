from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.generic import TemplateView
from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from home.models import *
from home.forms import *
from home.serializers import *
from common.helpers import *
from common.decorators import *


@login_required
@inspection_readable_required
def overview(request):
    aircrafts = Aircraft.objects.all().select_related('airframe')

    past_due_count = 0
    threshold_count = 0
    coming_due_count = 0

    # for aircraft in aircrafts:
    #     if aircraft.next_inspection_due is not None:
    #         next_due_date = aircraft.next_inspection_due[1]
    #         if is_past_due(next_due_date):
    #             past_due_count += 1
    #         elif is_within_threshold(next_due_date):
    #             threshold_count += 1
    #         else:
    #             coming_due_count += 1

    context = {
        'aircrafts': aircrafts,
        'past_due_count': past_due_count,
        'threshold_count': threshold_count,
        'coming_due_count': coming_due_count,
    }
    return render(request, 'overview.html', context)

@login_required
@inspection_readable_required
def aircraft_details(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('airframe'), reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'details.html', context)

@login_required
@inspection_readable_required
def aircraft_task_list(request, reg=''):
    aircraft = get_object_or_404(Aircraft.objects.select_related('inspection_program'), reg=reg)
    inspection_program = aircraft.inspection_program
    inspection_tasks = inspection_program.inspection_tasks.all() if inspection_program else []

    context = {
        'aircraft': aircraft,
        'inspection_program': inspection_program,
        'inspection_tasks': inspection_tasks,
    }
    return render(request, 'task_list.html', context)

@login_required
@inspection_readable_required
def aircraft_task(request, reg='', task_id=None):
    aircraft = get_object_or_404(Aircraft.objects.select_related('inspection_program'), reg=reg)
    inspection_task = get_object_or_404(InspectionTask, pk=task_id)

    context = {
        'aircraft': aircraft,
        'inspection_task': inspection_task,
        'inspection_task_name': str(inspection_task),
    }
    return render(request, 'task.html', context)

@login_required
@inspection_readable_required
def aircraft_mels(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)

    context = {
        'aircraft': aircraft,
    }
    return render(request, 'mels.html', context)

# maybe temporary
@login_required
@inspection_readable_required
def aircraft_assign_program(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)

    form = AssignInspectionProgramForm(request.POST or {
        'inspection_program': aircraft.inspection_program
    })
    if request.method == 'POST':
        if not can_write_inspection(request.user):
            return HttpResponseForbidden()
        if form.is_valid():
            inspection_program = form.cleaned_data.get('inspection_program')

            aircraft.inspection_program = inspection_program
            aircraft.save()

            for inspection_task in inspection_program.inspection_tasks.order_by('id'):
                for inspection_component in inspection_task.inspectioncomponent_set.order_by('id'):
                    for ic_type in InspectionComponentSubItem.TYPE_CHOICES:
                        type = ic_type[0]
                        try:
                            inspection_component_sub_item = InspectionComponentSubItem.objects.get(
                                type=type,
                                aircraft=aircraft,
                                inspection_component=inspection_component
                            )
                        except:
                            inspection_component_sub_item = InspectionComponentSubItem(
                                type=type,
                                aircraft=aircraft,
                                inspection_component=inspection_component,
                                interval=0
                            )
                            inspection_component_sub_item.save()

            return redirect('home:aircraft_task_list', reg=aircraft.reg)

    context = {
        'aircraft': aircraft,
        'form': form,
    }
    return render(request, 'assign_inspection_program.html', context)


class AircraftInspectionTaskView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, reg='', task_id=None):
        aircraft = get_object_or_404(Aircraft, reg=reg)
        inspection_task = get_object_or_404(InspectionTask, pk=task_id)

        task_serializer = InspectionTaskSerializer(inspection_task)
        task_data = task_serializer.data

        components_serializer = InspectionComponentSerializer(inspection_task.inspectioncomponent_set.order_by('id'), many=True)
        components_data = components_serializer.data

        return Response({
            'task': task_data,
            'components': components_data,
        })

    def post(self, request, reg='', task_id=None):
        aircraft = get_object_or_404(Aircraft, reg=reg)
        inspection_task = get_object_or_404(InspectionTask, pk=task_id)

        response = {
            'success': False,
        }

        component_id = request.data.get('component_id')
        sub_item_id = request.data.get('sub_item_id')
        field = request.data.get('field')
        value = request.data.get('value')

        try:
            inspection_component = inspection_task.inspectioncomponent_set.get(pk=component_id)
        except Exception as e:
            response['message'] = 'Invalid task component id'
            return Response(response)

        try:
            inspection_component_sub_item = inspection_component.inspectioncomponentsubitem_set.get(pk=sub_item_id)
        except Exception as e:
            response['message'] = 'Invalid task component sub item id'
            return Response(response)

        try:
            InspectionComponentSubItem._meta.get_field(field)
            setattr(inspection_component_sub_item, field, value)
            inspection_component_sub_item.save()
        except Exception as e:
            response['message'] = 'Failed to save data'
            return Response(response)

        response['success'] = True
        return Response(response)

