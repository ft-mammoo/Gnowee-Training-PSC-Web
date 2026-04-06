from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

class BaseViewPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class EnrollmentViewPagination(BaseViewPagination):
    page_size = 50

class StudentsAssignmentPagination(BaseViewPagination):
    page_size = 15

class StudentsExamsPagination(BaseViewPagination):
    page_size = 10
