from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.db import IntegrityError, transaction, connection
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
    """
    ViewSet for managing Teacher profiles and related academic metrics.
    
    Provides standard CRUD operations along with specialized actions for
    retrieving course assignments, teaching materials, and workload analytics.
    """
    queryset = Teacher.objects.all().select_related('user').order_by('-id')
    serializer_class = TeacherSerializer
    pagination_class = TeacherPagination #20 per page
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TeacherFilter
    search_fields = ['first_name', 'last_name', 'employee_code', 'email_institutional']
    ordering_fields = ['first_name', 'last_name', 'employee_code']

    # Override get_queryset to allow dynamic manager switching based on query parameters
    def get_queryset(self):
        """
        Dynamically switch the base manager if the client explicitly 
        filters by status. This delegates the actual value matching to DjangoFilterBackend
        """
        # if action is 'list' and 'status' is in query params, use the all_objects manager to include inactive records for filtering
        if self.action == 'list' and 'status' in self.request.query_params:
            return Teacher.all_objects.select_related('user').order_by('-id')
            
        # use the standard manager which hides inactive records
        return Teacher.objects.select_related('user').order_by('-id')

    @action(detail=True, methods=['get'])
    def courses(self, request, pk=None):
        """
        Retrieves all courses assigned to a specific teacher.
        
        Uses Prefetch objects to minimize database hits for the join table
        and annotates the student count directly in the query for performance.
        """
        teacher = self.get_object()

        # explicitly prefetching ONLY the CourseTeachers row that links to this specific teacher.
        # assign it to 'teacher_assignment' so my serializer can grab it instantly without hitting the DB again.
        teacher_assignment_qs = Prefetch(
            'course_teachers',
            queryset=CourseTeachers.objects.filter(teacher=teacher, status='a').order_by('-id'),
            to_attr='teacher_assignments'
        )

        # querying the Course table backwards through the join table.
        # using .annotate() to count active enrollments directly in PostgreSQL/SQLite.
        queryset = Course.objects.filter(
            course_teachers__teacher=teacher,
            course_teachers__status='a'
        ).annotate(
            student_count=Count(
                'enrollments',
                filter=~Q(enrollments__status='i'),
                distinct=True
            )
        ).prefetch_related(teacher_assignment_qs).distinct().order_by('-id')

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
        """
        Returns all teaching materials uploaded by a specific teacher.
        """
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
        """
        Lists all academic assignments created by a specific teacher.
        """
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
        """
        Calculates high-level teaching metrics across all active staff.
        
        Aggregates data for active courses, distinct student reach, 
        and pending grading tasks. Implements parent-state filtering to
        ensure metrics exclude assignments linked to inactive courses.
        """

        # subquery to count active courses for each teacher
        course_sq = CourseTeachers.objects.filter(
            teacher=OuterRef('pk'),
            status='a',          # The teacher-course mapping is active
            course__status='p'   # 'p' = Published / Active course
        ).values('teacher').annotate(
            count=Count('id', distinct=True)
        ).values('count')

        # subquery to count distinct students across all active courses for each teacher
        student_sq = Enrollment.objects.filter(
            course__course_teachers__teacher=OuterRef('pk'),
            course__course_teachers__status='a',
            course__status='p' # Only active courses
        ).exclude(status='i').values('course__course_teachers__teacher').annotate(
            count=Count('student', distinct=True)
        ).values('count')

        # subquery to count assignments for each teacher
        assignments_sq = Assignment.objects.filter(
            teacher=OuterRef('pk'),
            course__status='p'   # Only count assignments from active Published courses
        ).exclude(status='i').values('teacher').annotate(
            count=Count('id', distinct=True)
        ).values('count')

        # subquery to count pending submissions for each teacher
        pending_sq = Submission.objects.filter(
            assignment__teacher=OuterRef('pk'),
            assignment__course__status='p',  # Only count submissions from active Published courses
            status__in=['s', 'l']
        ).exclude(
            Q(status='i') | Q(assignment__status='i') # Exclude if submission OR assignment is inactive
        ).values('assignment__teacher').annotate(
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
    """
    Handles Department administration and Staff-to-Department assignments.
    """
    queryset = Department.objects.all().order_by('-id')
    serializer_class = DepartmentSerializer
    pagination_class = DepartmentPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DepartmentFilter

    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_date']

    @action(detail=True, methods=['get', 'post'])
    def teachers(self, request, pk=None):
        """
        Manages the relationship between Teachers and Departments.
        """
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
                    # Check if the user is already mapped to this department in any state active or inactive
                    # Use all_objects to find historical records for reactivation
                    queryset = UserDepartment.all_objects.filter(
                        department=department, 
                        user_id=user_id
                    ).order_by('-id')
                    # apply row-locking if the DB engine supports it, this prevents the NotSupportedError crash on SQLite
                    if connection.features.has_select_for_update:
                        queryset = queryset.select_for_update()

                    mapping = queryset.first()

                    if mapping:
                        if mapping.status == 'a':
                            return Response(
                                {"detail": "This user is already active in this department."},
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        # Reactivate existing record safely
                        # Use Serializer for reactivation to trigger validation and maintain consistency
                        serializer = UserDepartmentSerializer(
                            mapping, 
                            data={'status': 'a'}, 
                            partial=True, 
                            context={'request': request}
                        )
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
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
    """
    Manages the global list of professional qualifications.
    """
    queryset = Qualification.objects.all().order_by('-id')
    serializer_class = QualificationSerializer
    pagination_class = QualificationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = QualificationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserQualificationViewSet(viewsets.ModelViewSet):
    """
    Manages user-specific qualification assignments.
    """
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
    """
    Manages the global list of academic specializations.
    """
    queryset = Specialization.objects.all().order_by('-id')
    serializer_class = SpecializationSerializer
    pagination_class = SpecializationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SpecializationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserSpecializationViewSet(viewsets.ModelViewSet):
    """
    Manages user-specific specialization assignments.
    """
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
    """
    Manages the global list of job designations/titles.
    """
    queryset = Designation.objects.all().order_by('-id')
    serializer_class = DesignationSerializer
    pagination_class = DesignationPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DesignationFilter

    search_fields = ['name']
    ordering_fields = ['name', 'created_date']

class UserDesignationViewSet(viewsets.ModelViewSet):
    """
    Manages user-specific job designation assignments.
    """
    # exclude inactive designations
    queryset = UserDesignation.objects.exclude(
        designation__status='i'
    ).select_related('user', 'designation').order_by('-id')
    serializer_class = UserDesignationSerializer
    pagination_class = UserDesignationPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = UserDesignationFilter

    ordering_fields = ['user', 'designation', 'created_date']
