from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from inspection.models import *
from inspection.forms import *
from common.decorators import *


@login_required
@inspection_readable_required
def index(request):
    inspection_programs = InspectionProgram.objects.all()

    context = {
        'inspection_programs': inspection_programs,
    }
    return render(request, 'index.html', context)

@login_required
@inspection_readable_required
def inspection_program_details(request, program_id=None):
    inspection_program = get_object_or_404(InspectionProgram, pk=program_id)
    inspection_tasks = inspection_program.inspection_tasks.all()

    context = {
        'inspection_program': inspection_program,
        'inspection_tasks': inspection_tasks,
    }
    return render(request, 'program.html', context)

@login_required
@inspection_readable_required
def create_inspection_program(request):
    form = InspectionProgramForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('inspection:index')

    context = {
        'form': form,
    }
    return render(request, 'create_program.html', context)

@login_required
@inspection_readable_required
def add_inspection_task(request, program_id=None):
    inspection_program = get_object_or_404(InspectionProgram, pk=program_id)

    inspection_task_ids = [task.id for task in inspection_program.inspection_tasks.all()]
    form = AddTaskForm(request.POST or None, inspection_tasks=InspectionTask.objects.exclude(pk__in=inspection_task_ids))
    if request.method == 'POST':
        if form.is_valid():
            inspection_task = form.cleaned_data['inspection_task']
            inspection_program.inspection_tasks.add(inspection_task)
            return redirect('inspection:inspection_program_details', program_id=program_id)

    context = {
        'form': form,
        'inspection_program': inspection_program,
    }
    return render(request, 'add_task.html', context)
