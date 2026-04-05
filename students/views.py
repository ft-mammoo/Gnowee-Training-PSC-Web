from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Student
from .serializer import StudentSerializer, StudentEnrollmentModelSerializer
from courses.serializer import CourseSerializer
from utility.views import BaseViewPagination

class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status','gender','date_joined']
    search_fields = ['first_name', 'last_name', 'contact_number']
    ordering_fields = ['first_name', 'last_name', 'date_joined']
    pagination_class = BaseViewPagination

    def perform_destroy(self, instance):
        instance.status = 'i'
        instance.save()
    
    @action(detail=True, methods=['GET'])
    def courses(self, request, pk=None):
        student = self.get_object()
        courses = student.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = Student.objects.all().select_related('user')
        if self.request.query_params.get('courses'):
            queryset = queryset.prefetch_related('courses')
        return queryset
    
    @action(detail=False, methods=['GET'], url_path='with-courses')
    def with_courses(self, request):
        queryset = self.get_queryset().prefetch_related('courses')
        page = self.paginate_queryset(queryset)
        minimal_fields = ['id', 'first_name', 'last_name', 'courses']
        if page is not None:
            serializer = self.get_serializer(page, many=True, fields=minimal_fields)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True, fields=minimal_fields)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class StudentEnrollmentViewSet(ModelViewSet):
    serializer_class = StudentEnrollmentModelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'course', 'status', 'enrollment_date']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    
    def perform_destroy(self, instance):
        instance.status = 'i'
        instance.save()
