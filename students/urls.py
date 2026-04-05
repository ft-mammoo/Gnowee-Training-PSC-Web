from django.urls import path, include
from students import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('students', views.StudentViewSet, basename='student')
router.register('enrollments', views.StudentEnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]
