from django.shortcuts import render
from rest_framework.pagination import PageNumberPagination

class BasedViewPagination(PageNumberPagination):
    page_size = 5
