from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

class BaseViewPagination(PageNumberPagination):
    page_size = 20

class EnrollmentViewPagination(BaseViewPagination):
    page_size = 50
    max_page_size = 100
