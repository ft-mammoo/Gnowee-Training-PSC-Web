from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Prefetch, OuterRef, Subquery, IntegerField
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Teacher, Department, UserDepartment,
    Qualification, UserQualification, Specialization,
    UserSpecialization, Designation, UserDesignation
)
from .serializer import (
    TeacherSerializer, TeacherCourseListSerializer, TeacherMaterialSerializer,
    TeacherAssignmentSerializer, TeacherWorkloadSerializer, DepartmentSerializer,
    UserDepartmentSerializer, TeacherMinimalSerializer, QualificationSerializer,
    UserQualificationSerializer, SpecializationSerializer, UserSpecializationSerializer,
    DesignationSerializer, UserDesignationSerializer
)
from .filters import (
    TeacherFilter, TeacherCourseFilter, TeacherMaterialFilter,
    TeacherAssignmentFilter, TeacherWorkloadFilter, DepartmentFilter,
    QualificationFilter, UserQualificationFilter, SpecializationFilter,
    UserSpecializationFilter, DesignationFilter, UserDesignationFilter
)
from assessments.models import Assignment, Submission
from courses.models import Course, CourseTeachers, Material
from students.models import Enrollment
from utility.views import (
    TeacherPagination, TeacherMaterialPagination, DepartmentPagination,
    QualificationPagination, UserQualificationPagination, SpecializationPagination,
    UserSpecializationPagination, DesignationPagination, UserDesignationPagination
)

class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all().select_related('user').order_by('-id')
    serializer_class = TeacherSerializer
    pagination_class = TeacherPagination #20 per page
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TeacherFilter
    search_fields = ['first_name', 'last_name', 'employee_code', 'email_institutional']
    ordering_fields = ['first_name', 'last_name', 'employee_code']

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        teacher = self.get_object()

        # explicitly prefetching ONLY the CourseTeachers row that links to this specific teacher.
        # assign it to 'teacher_assignment' so my serializer can grab it instantly without hitting the DB again.
        teacher_assignment_qs = Prefetch(
            'course_teachers',
            queryset=CourseTeachers.objects.filter(teacher=teacher),
            to_attr='teacher_assignments'
        )

        # querying the Course table backwards through the join table.
        # using .annotate() to count active enrollments directly in PostgreSQL/SQLite.
        queryset = Course.objects.filter(course_teachers__teacher=teacher).annotate(
            student_count=Count(
                'enrollments',
                filter=~Q(enrollments__status='i'),
                distinct=True
            )
        ).prefetch_related(teacher_assignment_qs).order_by('-id')

        filterset = TeacherCourseFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TeacherCourseListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = TeacherCourseListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def materials(self, request, pk=None):
        teacher = self.get_object()
        queryset = Material.objects.filter(teacher=teacher).order_by('-id')

        filterset = TeacherMaterialFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        queryset = filterset.qs

        paginator = TeacherMaterialPagination() #25 per page
        page = paginator.paginate_queryset(queryset, request, view=self)
        if page is not None:
            serializer = TeacherMaterialSerializer(page, many=True, context={'request': request})
            return paginator.get_paginated_response(serializer.data)
        serializer = TeacherMaterialSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def assignments(self, request, pk=None):
        teacher = self.get_object()
        queryset = Assignment.objects.filter(teacher=teacher).order_by('-id')

        filterset = TeacherAssignmentFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TeacherAssignmentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = TeacherAssignmentSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='with-workload')
    def with_workload(self, request):

        # subquery to count active courses for each teacher
        course_sq = CourseTeachers.objects.filter(
            teacher=OuterRef('pk')
        ).exclude(status='i').values('teacher').annotate(
            count=Count('id', distinct=True)
        ).values('count')

        # subquery to count distinct students across all active courses for each teacher
        student_sq = Enrollment.objects.filter(
            course__course_teachers__teacher=OuterRef('pk'),
            course__course_teachers__status='a'
        ).exclude(status='i').values('course__course_teachers__teacher').annotate(
            count=Count('student', distinct=True)
        ).values('count')

        # subquery to count assignments for each teacher
        assignments_sq = Assignment.objects.filter(
            teacher=OuterRef('pk')
        ).exclude(status='i').values('teacher').annotate(
            count=Count('id', distinct=True)
        ).values('count')

        # subquery to count pending submissions for each teacher
        pending_sq = Submission.objects.filter(
            assignment__teacher=OuterRef('pk'),
            status__in=['s', 'l']
        ).exclude(status='i').values('assignment__teacher').annotate(
            count=Count('id', distinct=True)
        ).values('count')

        # using Coalesce to return 0 instead of None when there are no related records
        queryset = Teacher.objects.exclude(status='i').annotate(
            total_courses=Coalesce(Subquery(course_sq, output_field=IntegerField()), 0),
            total_students=Coalesce(Subquery(student_sq, output_field=IntegerField()), 0),
            total_assignments=Coalesce(Subquery(assignments_sq, output_field=IntegerField()), 0),
            pending_submissions=Coalesce(Subquery(pending_sq, output_field=IntegerField()), 0)
        ).order_by('-id')

        filterset = TeacherWorkloadFilter(request.query_params, queryset=queryset)
        if not filterset.is_valid():
            return Response(filterset.errors, status=400)
        queryset = filterset.qs

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = TeacherWorkloadSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = TeacherWorkloadSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializer
    pagination_class = DepartmentPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DepartmentFilter

    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date']

    @action(detail=True, methods=['get', 'post'])
    def teachers(self, request, pk=None):
        department = self.get_object()

        if request.method == 'GET':
            # filtering teachers who are actively linked to this department through the UserDepartment join table, and also ensuring the teacher themselves are active.
            queryset = Teacher.objects.filter(
                user__userdepartment__department=department,
                user__userdepartment__status='a',
                status='a'
            ).select_related('user').order_by('-id')

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = TeacherMinimalSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
            serializer = TeacherMinimalSerializer(queryset, many=True, context={'request': request})
            return Response(serializer.data)
        
        elif request.method == 'POST':

            user_id = request.data.get('user')
            if not user_id:
                return Response({"user": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                with transaction.atomic():
                    # check if the user is already active in this department
                    # # select_for_update() locks the row for this teacher-department pair
                    mapping = (
                        UserDepartment.all_objects
                        .select_for_update()
                        .filter(department=department, user_id=user_id)
                        .order_by('-id')
                        .first()
                    )
                    if mapping:
                        if mapping.status == 'a':
                            return Response(
                                {"detail": "This user is already active in this department."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        # Reactivate existing record safely
                        mapping.status = 'a'
                        mapping.save(update_fields=['status'])
                        serializer = UserDepartmentSerializer(mapping, context={'request': request})
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    
                    # if the user is not already active in this department, create a new record
                    data = request.data.copy()
                    data['department'] = department.id
                    serializer = UserDepartmentSerializer(data=data, context={'request': request})
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                # Catch collision where another thread created the record first
                return Response(
                    {"detail": "This user is already active in this department."},
                    status=status.HTTP_400_BAD_REQUEST
                )

class QualificationViewSet(viewsets.ModelViewSet):
    queryset = Qualification.objects.all().order_by('-id')
    serializer_class = QualificationSerializer
    pagination_class = QualificationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QualificationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserQualificationViewSet(viewsets.ModelViewSet):
    # exclude inactive qualifications
    queryset = UserQualification.objects.exclude(
        qualification__status='i'
    ).select_related('user', 'qualification').order_by('-id')
    serializer_class = UserQualificationSerializer
    pagination_class = UserQualificationPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserQualificationFilter

    ordering_fields = ['user', 'qualification', 'created_date']

class SpecializationViewSet(viewsets.ModelViewSet):
    queryset = Specialization.objects.all().order_by('-id')
    serializer_class = SpecializationSerializer
    pagination_class = SpecializationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SpecializationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserSpecializationViewSet(viewsets.ModelViewSet):
    # exclude inactive specializations
    queryset = UserSpecialization.objects.exclude(
        specialization__status='i'
    ).select_related('user', 'specialization').order_by('-id')
    serializer_class = UserSpecializationSerializer
    pagination_class = UserSpecializationPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserSpecializationFilter

    ordering_fields = ['user', 'specialization', 'created_date']

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all().order_by('-id')
    serializer_class = DesignationSerializer
    pagination_class = DesignationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DesignationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserDesignationViewSet(viewsets.ModelViewSet):
    # exclude inactive designations
    queryset = UserDesignation.objects.exclude(
        designation__status='i'
    ).select_related('user', 'designation').order_by('-id')
    serializer_class = UserDesignationSerializer
    pagination_class = UserDesignationPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserDesignationFilter

    ordering_fields = ['user', 'designation', 'created_date']
