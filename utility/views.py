from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

class BaseViewPagination(PageNumberPagination):
    page_size = 20
