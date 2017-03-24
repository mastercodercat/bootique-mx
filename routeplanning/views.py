from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from routeplanning.models import *
from routeplanning.forms import *


@login_required
def index(request):
    tails = Tail.objects.all()
    lines = Line.objects.all()

    context = {
        'tails': tails,
        'lines': lines,
    }
    return render(request, 'index_rp.html', context)

@login_required
def add_tail(request):
    form = TailForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-continue':
        return redirect('routeplanning:edit_tail', tail_id=tail.id)
    elif action_after_save == 'save-and-add-another':
        form = TailForm()

    if action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'tail.html', context)

@login_required
def edit_tail(request, tail_id=None):
    tail = get_object_or_404(Tail, pk=tail_id)

    form = TailForm(request.POST or None, instance=tail)
    if request.method == 'POST':
        if form.is_valid():
            tail = form.save()

    context = {
        'form': form,
    }
    return render(request, 'tail.html', context)

@login_required
def add_line(request):
    form = LineForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            line = Line(name=form.cleaned_data['name'])    
            line.save()

            for i in range(1, 12):
                entered_line_part_name = form.cleaned_data['part' + str(i)]
                if entered_line_part_name:
                    line_part = LinePart(name=entered_line_part_name, number=i, line=line)    
                    line_part.save()
                else:
                    break

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-continue':
        return redirect('routeplanning:edit_line', line_id=line.id)
    elif action_after_save == 'save-and-add-another':
        form = LineForm()

    if action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'line.html', context)

@login_required
def edit_line(request, line_id=None):
    line = get_object_or_404(Line, pk=line_id)

    initialData = {
        'name': line.name,
    }
    for line_part in line.linepart_set.all():
        initialData['part' + str(line_part.number)] = line_part.name

    form = LineForm(request.POST or initialData)
    if request.method == 'POST':
        if form.is_valid():
            if line.name != form.cleaned_data['name']:
                line.name = form.cleaned_data['name']
                line.save()

            for i in range(1, 12):
                entered_line_part_name = form.cleaned_data['part' + str(i)]
                if entered_line_part_name:
                    try:
                        line_part = line.linepart_set.get(number=i)
                        if line_part.name != entered_line_part_name:
                            line_part.name = entered_line_part_name
                            line_part.save()
                    except:
                        line_part = LinePart(name=entered_line_part_name, number=i, line=line)    
                        line_part.save()
                else:
                    break

    action_after_save = request.POST.get('action_after_save')

    if action_after_save == 'save-and-continue':
        return redirect('routeplanning:edit_line', line_id=line.id)
    elif action_after_save == 'save-and-add-another':
        form = LineForm()

    if action_after_save == 'save':
        return redirect('routeplanning:index')
    else:
        context = {
            'form': form,
        }
        return render(request, 'line.html', context)
