from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Student, Enrollment
from assessments.models import Assignment, Exams
from .serializer import StudentSerializer, StudentEnrollmentModelSerializer
from assessments.serializer import AssignmentSerializer, ExamsSerializer
from courses.serializer import CourseSerializer
from utility.views import BaseViewPagination, EnrollmentViewPagination, StudentsAssignmentPagination, StudentsExamsPagination

class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status','gender','date_joined']
    search_fields = ['first_name', 'last_name', 'contact_number']
    ordering_fields = ['first_name', 'last_name', 'date_joined']
    ordering = ['-date_joined']
    pagination_class = BaseViewPagination

    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=True, methods=['GET'])
    def courses(self, request, pk=None):
        student = self.get_object()
        courses = student.courses.all()
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def get_queryset(self):
        queryset = Student.objects.all().select_related('user')
        if not self.request.query_params.get('status'):
            queryset = queryset.filter(status='a')
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
    
    @action(detail=True, methods=['GET'], url_path='assignments')
    def assignments(self, request, pk=None):
        student = self.get_object()
        assignments = Assignment.objects.filter(course__in=student.courses.all()).select_related('course').order_by('id')
        paginator = StudentsAssignmentPagination()
        page = paginator.paginate_queryset(assignments, request)
        if page is not None:
            serializer = AssignmentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path='exams')
    def exams(self, request, pk=None):
        student = self.get_object()
        exams = Exams.objects.filter(course__in=student.courses.all()).select_related('course').order_by('id')
        paginator = StudentsExamsPagination()
        page = paginator.paginate_queryset(exams, request)
        if page is not None:
            serializer = ExamsSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = ExamsSerializer(exams, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class StudentEnrollmentViewSet(ModelViewSet):
    queryset = Enrollment.objects.select_related('student', 'course').all()
    serializer_class = StudentEnrollmentModelSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'course', 'status', 'enrollment_date']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    ordering_fields = ['enrollment_date', 'status']
    ordering = ['-enrollment_date']
    pagination_class = EnrollmentViewPagination
    
    def perform_destroy(self, instance):
        instance.delete()
