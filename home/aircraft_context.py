from home.models import AircraftType, Aircraft

def aircraft_in_types(context):
    aircraft_context_data = []
    aircraft_types = AircraftType.objects.all()
    for aircraft_type in aircraft_types:
        aircraft_in_type = aircraft_type.aircraft_set.all()
        aircraft_count = len(aircraft_in_type)
        if aircraft_count > 0:
            aircraft_context_data.append({
                'type': aircraft_type.type,
                'aircraft': aircraft_in_type,
            })

    return {
        'aircraft_data': aircraft_context_data,
    }
