from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from inspection.models import *
from inspection.forms import *


@login_required
def index(request):
    inspection_programs = InspectionProgram.objects.all()

    context = {
        'inspection_programs': inspection_programs,
    }
    return render(request, 'index.html', context)

@login_required
def inspection_program_details(request, program_id=None):
    inspection_program = get_object_or_404(InspectionProgram, pk=program_id)

    context = {
        'inspection_program': inspection_program,
    }
    return render(request, 'program.html', context)

@login_required
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
def create_inspection(request, program_id=None):
    inspection_program = get_object_or_404(InspectionProgram, pk=program_id)

    form = InspectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            inspection = form.save()
            inspection.inspection_program = inspection_program
            inspection.save()
            return redirect('inspection:inspection_program_details', program_id=program_id)

    context = {
        'form': form,
        'inspection_program': inspection_program,
    }
    return render(request, 'create_inspection.html', context)
