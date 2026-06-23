from django.urls import include, path
from rest_framework.routers import SimpleRouter

from assessments import views

router = SimpleRouter()
router.register("assignments", views.AssignmentViewSet, basename="assignment")
router.register("exams", views.ExamViewSet, basename="exam")
router.register("exam-answers", views.ExamAnswerViewSet, basename="exam-answer")
router.register("exam-answer-options", views.ExamAnswerOptionViewSet, basename="exam-answer-option")
router.register("exam-reviews", views.ExamReviewViewSet, basename="exam-review")
router.register("exam-submissions", views.ExamSubmissionViewSet, basename="exam-submission")
router.register("questions", views.QuestionViewSet, basename="question")
router.register("question-categories", views.QuestionCategoryViewSet, basename="question-category")
router.register("question-options", views.QuestionOptionViewSet, basename="question-option")
router.register("submissions", views.SubmissionViewSet, basename="submission")
router.register("submission-grades", views.SubmissionGradeViewSet, basename="submission-grade")

urlpatterns = [
    path("", include(router.urls)),
]
