from django.urls import include, path
from students import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('students', views.StudentViewSet, basename='student')


urlpatterns = [
    # ViewSet Urls
    path('', include(router.urls)),
]
