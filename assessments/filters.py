import django_filters

from assessments.models import (
    Assignment,
    ExamQuestions,
    ExamReviews,
    Exams,
    ExamSubmissions,
    QuestionOptions,
    Submission,
    SubmissionGrade,
)


class AssignmentFilter(django_filters.FilterSet):
    # Cast datetime to date for clean YYYY-MM-DD matching
    created_date = django_filters.DateFilter(field_name="created_date", lookup_expr="date")
    due_date = django_filters.DateFilter(field_name="due_date")

    class Meta:
        model = Assignment
        fields = ["course", "teacher", "due_date", "created_date"]


class ExamFilter(django_filters.FilterSet):
    start_time = django_filters.DateFilter(field_name="start_time", lookup_expr="date")
    end_time = django_filters.DateFilter(field_name="end_time", lookup_expr="date")

    class Meta:
        model = Exams
        fields = ["course", "start_time", "end_time"]


class QuestionFilter(django_filters.FilterSet):
    class Meta:
        model = ExamQuestions
        fields = ["category", "question_type"]


class QuestionOptionFilter(django_filters.FilterSet):
    class Meta:
        model = QuestionOptions
        fields = ["question", "is_correct"]


class ExamSubmissionFilter(django_filters.FilterSet):
    submission_time = django_filters.DateFilter(field_name="submission_time", lookup_expr="date")

    class Meta:
        model = ExamSubmissions
        fields = ["exam", "student", "submission_time"]


class SubmissionFilter(django_filters.FilterSet):
    submitted_date = django_filters.DateFilter(field_name="submitted_date", lookup_expr="date")

    class Meta:
        model = Submission
        fields = ["assignment", "student", "status", "submitted_date"]


class SubmissionGradeFilter(django_filters.FilterSet):
    created_date = django_filters.DateFilter(field_name="created_date")

    class Meta:
        model = SubmissionGrade
        fields = ["submission", "graded_by", "created_date"]


class ExamReviewFilter(django_filters.FilterSet):
    class Meta:
        model = ExamReviews
        fields = ["exam_submission", "graded_by"]
