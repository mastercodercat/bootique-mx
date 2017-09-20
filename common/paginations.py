from rest_framework.pagination import LimitOffsetPagination


class DataTablePagination(LimitOffsetPagination):
    offset_query_param = 'start'
    limit_query_param = 'length'
