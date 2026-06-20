import django_filters

from assessments.models import Submission, SubmissionGrade


class SubmissionFilter(django_filters.FilterSet):
    # Cast the datetime field to a date for clean string matching (YYYY-MM-DD)
    submitted_date = django_filters.DateFilter(field_name="submitted_date", lookup_expr="date")

    class Meta:
        model = Submission
        fields = ["assignment", "student", "status", "submitted_date"]


class SubmissionGradeFilter(django_filters.FilterSet):
    # Cast the datetime field to a date for clean string matching (YYYY-MM-DD)
    created_date = django_filters.DateFilter(field_name="created_date")

    class Meta:
        model = SubmissionGrade
        fields = ["submission", "graded_by", "created_date"]
