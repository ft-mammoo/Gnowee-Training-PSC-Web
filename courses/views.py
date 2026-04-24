import django_filters
from django.db.models import Prefetch, Q, Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins

from assessments.models import Assignment, Exams
from assessments.serializer import AssignmentSerializer, AssignmentNestedSerializer, ExamsSerializer, ExamNestedSerializer
from courses import models, serializer
from staffs.models import Teacher
from staffs.serializer import TeacherNameSerializer
from students.models import Student, Enrollment
from utility.views import (
    BaseViewPagination, CourseStatsPagination, CourseStudentsPagination, CourseTeachersPagination,
    StudentsAssignmentPagination, StudentsExamsPagination, MaterialPagination
)

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
        course = get_object_or_404(self.get_queryset(), pk=pk)

        # We prefetch enrollments for this course to avoid N+1 queries when accessing enrollment data in the serializer
        enrollment_qs = Enrollment.all_objects.filter(course=course)
        qs = Student.objects.filter(enrollments__course=course).select_related('user').prefetch_related(
            Prefetch('enrollments', queryset=enrollment_qs, to_attr='current_course_enrollment')
        ).distinct().order_by('id')

        # 2. Filtering logic based on query parameters
        e_status = request.query_params.get('enrollment_status')
        if e_status:
            qs = qs.filter(enrollments__status=e_status, enrollments__course=course)
            
        s_status = request.query_params.get('student_status')
        if s_status:
            qs = qs.filter(status=s_status)

        # 3. Search functionality on first_name and last_name
        search = request.query_params.get('search')
        if search:
            qs = qs.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search))

        # 4. Pagination and serialization
        paginator = CourseStudentsPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            se = serializer.StudentWithEnrollmentSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(se.data)
        se = serializer.StudentWithEnrollmentSerializer(qs, many=True, context={'request': request})
        return Response(data=se.data, status=status.HTTP_200_OK)
    @action(methods=["GET", "POST"], detail=True)
    def teachers(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)

        if request.method == "GET":
            qs = Teacher.objects.filter(
                teacher_courses__course=course,
                teacher_courses__status='a'
            ).select_related('user').distinct().order_by('id')
            se = TeacherNameSerializer(qs, many=True, context={'request': request})
            return Response(data=se.data, status=status.HTTP_200_OK)
            
        elif request.method == "POST":
            data = request.data.copy()
            data['course'] = pk
            teacher_id = data.get('teacher')
            if teacher_id and models.CourseTeachers.objects.filter(
                course=course, 
                teacher_id=teacher_id, 
                status='a'
            ).exists():
                return Response(
                    {"detail": "This teacher is already assigned to this course."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            se = serializer.CourseTeacherSerializer(data=data, context={'request': request})
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
        
    @action(methods=["GET", "POST"], detail=True)
    def materials(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)

        if request.method == "GET":
            qs = models.Material.objects.filter(course=course).select_related('teacher').order_by('id')
            m_type = request.query_params.get('type')
            if m_type:
                qs = qs.filter(type=m_type)
            
            status_param = request.query_params.get('status')
            if status_param:
                qs = qs.filter(status=status_param)
            search = request.query_params.get('search')
            if search:
                qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

            upload_date = request.query_params.get('upload_date')
            if upload_date:
                qs = qs.filter(uploaded_at=upload_date)

            paginator = BaseViewPagination()
            page = paginator.paginate_queryset(qs, request)
            if page is not None:
                se = serializer.MaterialNestedSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response(se.data)
            se = serializer.MaterialNestedSerializer(qs, many=True, context={'request': request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            data = request.data.copy()
            data['course'] = pk
            se = serializer.MaterialSerializer(data=data, context={'request': request})
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=["GET", "POST"], detail=True)
    def assignments(self, request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        if request.method == "GET":
            qs = Assignment.objects.filter(course=course).select_related('teacher').order_by('id')
            
            due_date = request.query_params.get('due_date')
            if due_date:
                qs = qs.filter(due_date=due_date)
            
            teacher = request.query_params.get('teacher')
            if teacher:
                qs = qs.filter(teacher_id=teacher)
            
            paginator = StudentsAssignmentPagination()
            page = paginator.paginate_queryset(qs, request)
            if page is not None:
                se = AssignmentNestedSerializer(page, many=True, context={'request': request})
                return paginator.get_paginated_response(se.data)
            se = AssignmentNestedSerializer(qs, many=True, context={'request': request})
            return Response(data=se.data, status=status.HTTP_200_OK)
        
        elif request.method == "POST":
            data = request.data.copy()
            data['course']=pk
            se = AssignmentSerializer(data=data, context={'request': request})
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=["GET"], detail=True)
    def exams(self,request, pk=None):
        course = get_object_or_404(self.get_queryset(), pk=pk)
        qs = Exams.objects.filter(course=course, status='a').annotate(
            question_count=Count('exam_questions', filter=~Q(exam_questions__status='i'), distinct=True)
        ).order_by('id')

        start_time = request.query_params.get('start_time')
        if start_time:
            qs = qs.filter(start_time__gte=start_time)

        end_time = request.query_params.get('end_time')
        if end_time:
            qs = qs.filter(end_time__lte=end_time)

        paginator = StudentsExamsPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            se = ExamNestedSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(se.data)
        se = ExamNestedSerializer(qs, many=True, context={'request': request})
        return Response(data=se.data, status=status.HTTP_200_OK)
    
    @action(methods=["GET"], detail=False, url_path='with-stats')
    def with_stats(self, request):
        qs = models.Course.objects.annotate(
            total_students=Count('enrollments', filter=~Q(enrollments__status='i'), distinct=True),
            active_students=Count('enrollments', filter=Q(enrollments__status='a'), distinct=True),
            total_teachers=Count('course_teachers', filter=~Q(course_teachers__status='i'), distinct=True),
            total_materials=Count('materials', filter=~Q(materials__status='i'), distinct=True),
            total_assignments=Count('assignment', filter=~Q(assignment__status='i'), distinct=True)
        ).order_by('id')

        stat_status = request.query_params.get('status')
        if stat_status:
            qs = qs.filter(status=stat_status)

        paginator = CourseStatsPagination()
        page = paginator.paginate_queryset(qs, request)
        if page is not None:
            se = serializer.CourseStatsSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(se.data)
        se = serializer.CourseStatsSerializer(qs, many=True, context={'request': request})
        return Response(data=se.data, status=status.HTTP_200_OK)

class MaterialFilter(django_filters.FilterSet):
    upload_date = django_filters.DateFilter(field_name='uploaded_at', lookup_expr='date')
    class Meta:
        model = models.Material
        fields = ['course', 'type', 'status', 'teacher', 'upload_date']

class MaterialViewSet(ModelViewSet):
    queryset = models.Material.objects.all().select_related('course', 'teacher').order_by('id')
    pagination_class = MaterialPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MaterialFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'uploaded_at']
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializer.MaterialListSerializer
        return serializer.MaterialSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

class CourseTeacherFilter(django_filters.FilterSet):
    class Meta:
        model = models.CourseTeachers
        fields = ['course', 'teacher', 'status']

class CourseTeacherViewSet(mixins.ListModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = models.CourseTeachers.objects.all().select_related('course', 'teacher__user').order_by('id')
    serializer_class = serializer.CourseTeacherSerializer
    pagination_class = CourseTeachersPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = CourseTeacherFilter
    ordering_fields = ['created_date']
