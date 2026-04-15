import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from courses import models, serializer
from students.models import Student
from students.serializer import StudentSerializer
from utility.views import BaseViewPagination

class CourseFilter(django_filters.FilterSet):
    class Meta:
        model = models.Course
        fields = ['status', 'created_date']

class CourseViewSet(ModelViewSet):
    queryset = models.Course.objects.all().order_by('id')
    serializer_class = serializer.CourseSerializer
    pagination_class = BaseViewPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_date']
    @action(methods=["GET"], detail=True)
    def students(self, request, pk=None):
        qs = Student.objects.filter(enrollments__course__id=pk)
        se = StudentSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)
    @action(methods=["GET", "POST"], detail=True)
    def teachers(self, request, pk=None):
        course = self.get_object()
        if request.method == "GET":
            teachers = models.CourseTeachers.objects.filter(course=course)
            se = serializer.CourseTeacherSerializer(teachers, many=True)
            return Response(data=se.data, status=status.HTTP_200_OK)
        elif request.method == "POST":
            data = request.data.copy()
            data['course'] = pk
            se = serializer.CourseTeacherSerializer(data=data)
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
