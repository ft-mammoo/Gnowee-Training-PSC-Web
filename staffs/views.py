from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Teacher
from .serializer import TeacherSerializer
from .filters import TeacherFilter
from utility.views import TeacherPagination

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().select_related('user').order_by('-id')
    serializer_class = TeacherSerializer
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TeacherFilter
    search_fields = ['first_name', 'last_name', 'employee_code', 'email_institutional']
    ordering_fields = ['first_name', 'last_name', 'employee_code']
