from django.shortcuts import render, redirect
from django.http import Http404

from rest_framework import views
from rest_framework import generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from common.helpers import *
from common.exceptions import APIException
from common.paginations import DataTablePagination

from routeplanning.models import Revision


def index_redirect(request):
    if request.user.is_authenticated():
        if can_read_gantt(request.user):
            return redirect('routeplanning:view_current_published_gantt')
        # elif can_read_inspection(request.user):
        #     return redirect('home:overview')
        else:
            return render(request, 'home-empty.html')
    else:
        return redirect('account_login')


class APICallMixin(object):
    def call_method(self, method, *args, **kwargs):
        try:
            method_to_call = getattr(self, method)
            response = method_to_call(*args, **kwargs)
            response['success'] = True
            return Response(response)
        except APIException as error:
            return Response({
                'success': False,
                'error': str(error)
            }, status=error.status)


class GanttRevisionMixin(object):
    def get_revision(self, revision_id):
        if revision_id and int(revision_id) > 0:
            try:
                return Revision.objects.get(pk=revision_id)
            except Revision.DoesNotExist:
                raise APIException('Revision not found', status=400)
        else:
            return None


class APIView(views.APIView, APICallMixin):
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


class DataTablePaginatedListView(ListAPIView):
    pagination_class = DataTablePagination

    def get_total_count(self):
        raise NotImplementedError('Please implement `get_total_count` method')

    def get(self, *args, **kwargs):
        response = super(DataTablePaginatedListView, self).get(*args, **kwargs)

        draw = self.request.session.get('flights_dt_page_draw', 1)
        draw = draw + 1
        self.request.session['flights_dt_page_draw'] = draw

        original_data = response.data
        data = {
            'success': True,
            "recordsTotal": self.get_total_count(),
            "recordsFiltered": original_data['count'],
            "draw": draw,
            "data": original_data['results']
        }
        return Response(data)


class RetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    error_message = 'Error occurred'

    def delete(self, *args, **kwargs):
        result = {
            'success': False,
        }

        try:
            super(RetrieveDestroyAPIView, self).delete(*args, **kwargs)
            result['success'] = True
        except:
            result['error'] = self.error_message

        return Response(result)
