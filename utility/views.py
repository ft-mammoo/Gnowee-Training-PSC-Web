from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

class BaseViewPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None

class EnrollmentViewPagination(BaseViewPagination):
    page_size = 50

class StudentsAssignmentPagination(BaseViewPagination):
    page_size = 15

class StudentsExamsPagination(BaseViewPagination):
    page_size = 10

class CourseStudentsPagination(BaseViewPagination):
    page_size = 30

class CourseStatsPagination(BaseViewPagination):
    page_size = 15

class MaterialPagination(BaseViewPagination):
    page_size = 30

class CourseTeachersPagination(BaseViewPagination):
    page_size = 50

class TeacherPagination(BaseViewPagination):
    page_size = 20

class TeacherMaterialPagination(BaseViewPagination):
    page_size = 25

class DepartmentPagination(BaseViewPagination):
    page_size = 30

class QualificationPagination(BaseViewPagination):
    page_size = 20

class UserQualificationPagination(BaseViewPagination):
    page_size = 50

class SpecializationPagination(BaseViewPagination):
    page_size = 20

class UserSpecializationPagination(BaseViewPagination):
    page_size = 50

class DesignationPagination(BaseViewPagination):
    page_size = 20

class UserDesignationPagination(BaseViewPagination):
    page_size = 50
