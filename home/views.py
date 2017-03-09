from django.shortcuts import render
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    return render(request, 'test.html')

@login_required
def overview(request):
    return render(request, 'overview.html')

@login_required
def aircraft_details(request, aircraft=''):
    return render(request, 'aircraft_details.html')
