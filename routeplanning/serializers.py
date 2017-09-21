from django.urls import reverse

from rest_framework import serializers

from common.helpers import totimestamp
from routeplanning.models import Flight
from routeplanning.models import Hobbs


class DataTableFlightSerializer(serializers.ModelSerializer):
    def to_representation(self, flight):
        flight_edit_link = reverse('routeplanning:edit_flight', kwargs={ 'flight_id': flight.id })
        buttons = '<span style="white-space: nowrap;">'
        buttons += '<a href="' + flight_edit_link + '" class="btn btn-primary btn-xs"><i class="fa fa-fw fa-edit"></i></a> '
        buttons += '<a href="javascript:void();" class="btn-delete-flight btn btn-danger btn-xs"><i class="fa fa-fw fa-trash"></i></a>'
        buttons += '</span>'
        return (
            flight.id,
            flight.number,
            flight.origin,
            flight.destination,
            totimestamp(flight.scheduled_out_datetime) if flight.scheduled_out_datetime else '',
            totimestamp(flight.scheduled_off_datetime) if flight.scheduled_off_datetime else '',
            totimestamp(flight.scheduled_on_datetime) if flight.scheduled_on_datetime else '',
            totimestamp(flight.scheduled_in_datetime) if flight.scheduled_in_datetime else '',
            totimestamp(flight.estimated_out_datetime) if flight.estimated_out_datetime else '',
            totimestamp(flight.estimated_off_datetime) if flight.estimated_off_datetime else '',
            totimestamp(flight.estimated_on_datetime) if flight.estimated_on_datetime else '',
            totimestamp(flight.estimated_in_datetime) if flight.estimated_in_datetime else '',
            totimestamp(flight.actual_out_datetime) if flight.actual_out_datetime else '',
            totimestamp(flight.actual_off_datetime) if flight.actual_off_datetime else '',
            totimestamp(flight.actual_on_datetime) if flight.actual_on_datetime else '',
            totimestamp(flight.actual_in_datetime) if flight.actual_in_datetime else '',
            buttons,
        )

    class Meta:
        model = Flight
        fields = (
            'number', 'origin', 'destination', 'type',
            'scheduled_out_datetime', 'scheduled_in_datetime', 'scheduled_off_datetime', 'scheduled_on_datetime',
            'estimated_out_datetime', 'estimated_in_datetime', 'estimated_off_datetime', 'estimated_on_datetime',
            'actual_out_datetime', 'actual_in_datetime', 'actual_off_datetime', 'actual_on_datetime'
        )


class HobbsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hobbs
        fields = ('pk', 'hobbs_time', 'type', 'hobbs', 'tail')
