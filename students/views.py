from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from students.models import Student
from students.serializer import StudentModelSerializer, StudentWithCoursesSerializer,StudentCourseSerializer,StudentAssignmentSerializer,StudentExamSerializer
from utility.pagination import DynamicPageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from assessments.models import Assignment, Exams

class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentModelSerializer
    pagination_class = DynamicPageNumberPagination

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'gender', 'date_joined']
    search_fields = ['first_name', 'last_name', 'contact_number']                                          

    def get_page_size(self):
        return 20
    @action(detail=True, methods=['get'], url_path='with-courses')
    def with_courses(self, request, pk):
        student = self.get_object()
        serializer = StudentWithCoursesSerializer(student)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def courses(self, request, pk):
        student = self.get_object()
        serializer = StudentCourseSerializer(student.courses.all(), many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk):
        student = self.get_object()
        assignments = Assignment.objects.filter(course__in=student.courses.all())
        serializer = StudentAssignmentSerializer(assignments, many=True, context={'student': student})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def exams(self, request, pk):
        student = self.get_object()
        exams = Exams.objects.filter(course__in=student.courses.all())
        serializer = StudentExamSerializer(exams, many=True, context={'student': student})
        return Response(serializer.data)
