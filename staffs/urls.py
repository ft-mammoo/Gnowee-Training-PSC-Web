from django.urls import path, include
from rest_framework.routers import SimpleRouter
from staffs import views

router = SimpleRouter()
router.register('teachers', views.TeacherViewSet, basename='teacher')
router.register('departments', views.DepartmentViewSet, basename='department')

urlpatterns = [
    path('', include(router.urls)),
]
