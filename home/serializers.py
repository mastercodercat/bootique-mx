from rest_framework import serializers

from home.models import InspectionComponentSubItem
from inspection.models import *


class InspectionTaskSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()

    class Meta:
        model = InspectionTask
        fields = ('number', 'name', 'target')

    def get_target(self, obj):
        return InspectionTask.TARGET_STRINGS[obj.target]


class InspectionComponentSubItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = InspectionComponentSubItem
        fields = ('type', 'interval', 'CW', 'TSX_adj', 'max_limit')

    def get_type(self, obj):
        return InspectionComponentSubItem.TYPE_STRINGS[obj.type]


class InspectionComponentSerializer(serializers.ModelSerializer):
    inspectioncomponentsubitem_set = InspectionComponentSubItemSerializer(many=True, read_only=True)

    class Meta:
        model = InspectionComponent
        fields = ('pn', 'sn', 'name', 'inspectioncomponentsubitem_set')
