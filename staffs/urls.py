from django.urls import path, include
from rest_framework.routers import SimpleRouter
from staffs import views

router = SimpleRouter()
router.register('teachers', views.TeacherViewSet, basename='teacher')
router.register('departments', views.DepartmentViewSet, basename='department')
router.register('qualifications', views.QualificationViewSet, basename='qualification')
router.register('user-qualifications', views.UserQualificationViewSet, basename='user-qualification')
router.register('specializations', views.SpecializationViewSet, basename='specialization')
router.register('user-specializations', views.UserSpecializationViewSet, basename='user-specialization')

urlpatterns = [
    path('', include(router.urls)),
]
