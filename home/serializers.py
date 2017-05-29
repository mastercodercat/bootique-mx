from rest_framework import serializers

from home.models import InspectionComponentSubItem
from inspection.models import *


class InspectionTaskSerializer(serializers.ModelSerializer):
    target = serializers.SerializerMethodField()

    class Meta:
        model = InspectionTask
        fields = ('id', 'number', 'name', 'target')

    def get_target(self, obj):
        return InspectionTask.TARGET_STRINGS[obj.target]


class InspectionComponentSubItemSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    class Meta:
        model = InspectionComponentSubItem
        fields = ('id', 'type', 'interval', 'CW', 'TSX_adj', 'max_limit')

    def get_type(self, obj):
        return InspectionComponentSubItem.TYPE_STRINGS[obj.type]


class InspectionComponentSerializer(serializers.ModelSerializer):
    sub_items = serializers.SerializerMethodField()

    class Meta:
        model = InspectionComponent
        fields = ('id', 'pn', 'sn', 'name', 'sub_items')
    
    def get_sub_items(self, obj):
        query_set = obj.inspectioncomponentsubitem_set.order_by('type')
        return InspectionComponentSubItemSerializer(query_set, many=True).data
