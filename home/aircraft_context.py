from django.shortcuts import render, get_object_or_404

from home.models import AircraftType, Aircraft


def aircraft_in_types(context, reg = ''):
    aircraft_context_data = []
    aircraft_types = AircraftType.objects.all()
    for aircraft_type in aircraft_types:
        aircraft_in_type = aircraft_type.aircraft_set.all().order_by('reg')
        aircraft_count = len(aircraft_in_type)
        if aircraft_count > 0:
            aircraft_context_data.append({
                'type': aircraft_type.type,
                'aircraft': aircraft_in_type,
            })

    template_context = {
        'aircraft_data': aircraft_context_data,
    }

    url_name = context.resolver_match.url_name

    try:
        reg = context.resolver_match.kwargs['reg']
        aircraft = get_object_or_404(Aircraft.objects.select_related('type'), reg=reg)
        template_context['current_aircraft_type'] = aircraft.type.type
        template_context['current_aircraft_reg'] = reg
    except:
        pass

    return template_context
