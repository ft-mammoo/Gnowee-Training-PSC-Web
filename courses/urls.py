from django.urls import include, path
from courses import views

urlpatterns = [
    # Function-based Views Urls
    path('fb/courses/', views.course_view, name='course_view'),
    path('fb/courses/<int:pk>/', views.course_detail_view, name='course_detail_fb_view'),
    path('fb/courses/<int:pk>/<str:action>/', views.course_actions_view, name='course_detail_fb_view'),
]