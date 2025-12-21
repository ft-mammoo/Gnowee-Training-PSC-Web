from django.urls import include, path
from courses import views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register('courses', views.CourseViewSet, basename='course')

urlpatterns = [
    # Function-based Views Urls
    path('fb/courses/', views.course_view, name='course_view'),
    path('fb/courses/<int:pk>/', views.course_detail_view, name='course_detail_fb_view'),
    path('fb/courses/<int:pk>/<str:action>/', views.course_actions_view, name='course_detail_fb_view'),
    # Class-based Views Urls
    path('cb/courses/', views.CourseView.as_view(), name='course_view'),
    path('cb/courses/<int:pk>/', views.CourseDetailedView.as_view(), name='course_detail_cb_view'),
    path('cb/courses/<int:pk>/<str:action>/', views.CourseActionsView.as_view(), name='course_detail_cb_view'),
    # Generic Class-based Views Urls
    path('gen/courses/', views.CourseGenericView.as_view(), name='course_generic_view'),
    path('gen/courses/<int:pk>/', views.CourseDetailGenericView.as_view(), name='course_detail_generic_view'),
    # ViewSet Urls
    path('', include(router.urls)),
]