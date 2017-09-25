from django.core.exceptions import PermissionDenied
from django.views.generic import base
from django.views.generic import edit

from rest_framework import views
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.helpers import *
from common.exceptions import APIException
from common.paginations import DataTablePagination


class PermissionMixin(object):
    def check_permissions(self):
        if self.permission_classes:
            for permission_class in self.permission_classes:
                permission = permission_class()
                if not permission.has_permission(self.request, self):
                    raise PermissionDenied


class GetPermissionMixin(object):
    def get(self, *args, **kwargs):
        self.check_permissions()
        return super(GetPermissionMixin, self).get(*args, **kwargs)


class PostPermissionMixin(object):
    def post(self, *args, **kwargs):
        self.check_permissions()
        return super(PostPermissionMixin, self).post(*args, **kwargs)


class APICallMixin(object):
    def call_method(self, method, *args, **kwargs):
        try:
            method_to_call = getattr(self, method)
            return Response(method_to_call(*args, **kwargs))
        except APIException as error:
            if error.response:
                response = error.response
                response['error'] = error.detail
                return Response(response, status=error.status)
            else:
                return Response({
                    'error': error.detail
                }, status=error.status)

    def call_super_method(self, method, error_message, *args, **kwargs):
        try:
            method_to_call = getattr(super(APICallMixin, self), method)
            return method_to_call(*args, **kwargs)
        except:
            return Response({
                'error': error_message
            }, status=500)


class APIView(APICallMixin, views.APIView):
    def get(self, *args, **kwargs):
        return self.call_method('_get', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.call_method('_post', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.call_method('_put', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.call_method('_delete', *args, **kwargs)

    def _get(self, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def _post(self, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def _put(self, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def _delete(self, *args, **kwargs):
        raise MethodNotAllowed('DELETE')


class ListAPIView(generics.ListAPIView):
    pass


class ListCreateAPIView(generics.ListCreateAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    create_error_message = 'Error occurred'

    def get(self, *args, **kwargs):
        return self.call_super_method('get', None, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.call_super_method('post', self.create_error_message, *args, **kwargs)


class DataTablePaginatedListView(APICallMixin, ListAPIView):
    pagination_class = DataTablePagination

    def get_total_count(self):
        raise NotImplementedError('Please implement `get_total_count` method')

    def _get(self, *args, **kwargs):
        response = super(DataTablePaginatedListView, self).get(*args, **kwargs)

        draw = self.request.session.get('flights_dt_page_draw', 1)
        draw = draw + 1
        self.request.session['flights_dt_page_draw'] = draw

        original_data = response.data
        data = {
            "recordsTotal": self.get_total_count(),
            "recordsFiltered": original_data['count'],
            "draw": draw,
            "data": original_data['results']
        }
        return data

    def get(self, *args, **kwargs):
        return self.call_method('_get', *args, **kwargs)


class RetrieveDestroyAPIView(APICallMixin, generics.RetrieveDestroyAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    retrieve_error_message = 'Error occurred'
    delete_error_message = 'Error occurred'

    def get(self, *args, **kwargs):
        return self.call_super_method('get', self.retrieve_error_message, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.call_super_method('delete', self.delete_error_message, *args, **kwargs)


class TemplateView(PermissionMixin, GetPermissionMixin, base.TemplateView):
    pass


class FormView(PermissionMixin, GetPermissionMixin, PostPermissionMixin, edit.FormView):
    def get(self, *args, **kwargs):
        self.check_permissions()
        return super(FormView, self).get(*args, **kwargs)

    def post(self, *args, **kwargs):
        self.check_permissions()
        return super(FormView, self).post(*args, **kwargs)


class CreateView(PermissionMixin, GetPermissionMixin, PostPermissionMixin, edit.CreateView):
    pass


class UpdateView(PermissionMixin, GetPermissionMixin, PostPermissionMixin, edit.UpdateView):
    pass
