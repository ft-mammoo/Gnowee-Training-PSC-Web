from django.urls import path, include
from rest_framework.routers import SimpleRouter
from assessments import views

router = SimpleRouter()
router.register('exams', views.ExamViewSet, basename='exam')
router.register('questions', views.QuestionViewSet, basename='question')
router.register('question-options', views.QuestionOptionViewSet, basename='question-option')
router.register('exam-question-mappings', views.ExamQuestionMappingViewSet, basename='exam-question-mapping')

urlpatterns = [
    path('', include(router.urls)),
]