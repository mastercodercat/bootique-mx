from rest_framework import permissions

from common.helpers import can_read_gantt
from common.helpers import can_write_gantt


class GanttReadPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return can_read_gantt(request.user)


class GanttWritePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return can_write_gantt(request.user)
