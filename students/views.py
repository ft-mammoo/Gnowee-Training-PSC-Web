from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Student
from .serializer import StudentSerializer
from courses.serializer import CourseSerializer

class StudentViewSet(ModelViewSet):
    serializer_class = StudentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status','gender','date_joined']
    search_fields = ['first_name', 'last_name', 'contact_number']
    ordering_fields = ['first_name', 'last_name', 'date_joined']

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
