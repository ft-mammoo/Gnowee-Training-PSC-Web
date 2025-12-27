from rest_framework.viewsets import ModelViewSet
from students.models import Student
from students.serializer import StudentModelSerializer
from utility.pagination import DynamicPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentModelSerializer
    pagination_class = DynamicPageNumberPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'gender', 'date_joined']
    search_fields = ['first_name', 'last_name', 'contact_number']                                          

    def get_page_size(self):
        return 20
