from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from home.models import Aircraft


@login_required
def index(request):
    return render(request, 'test.html')

@login_required
def overview(request):
    return render(request, 'overview.html')

@login_required
def aircraft_details(request, reg=''):
    aircraft = get_object_or_404(Aircraft, reg=reg)
    context = {
        'aircraft': aircraft,
    }
    return render(request, 'aircraft_details.html', context)
