from django.urls import include, path
from courses import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('courses', views.CourseViewSet, basename='course')
router.register('materials', views.MaterialViewSet, basename='material')

urlpatterns = [
    path('', include(router.urls)),
]
