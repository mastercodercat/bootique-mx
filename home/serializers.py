from rest_framework import serializers

from home.models import InspectionComponentSubItem
from inspection.models import *


class InspectionTaskSerializer(serializers.ModelSerializer):

  class Meta:
    model = InspectionTask
    fields = ('number', 'name')


class InspectionComponentSubItemSerializer(serializers.ModelSerializer):

  class Meta:
    model = InspectionComponentSubItem
    fields = ('type', 'interval', 'CW', 'TSX_adj', 'max_limit')


class InspectionComponentSerializer(serializers.ModelSerializer):
  inspectioncomponentsubitem_set = InspectionComponentSubItemSerializer(many=True, read_only=True)

  class Meta:
    model = InspectionComponent
    fields = ('pn', 'sn', 'name', 'inspectioncomponentsubitem_set')
