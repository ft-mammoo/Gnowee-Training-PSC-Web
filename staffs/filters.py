import django_filters
from .models import Teacher

class TeacherFilter(django_filters.FilterSet):
    # Define filters for the Teacher model
    date_joined = django_filters.DateFilter(field_name='date_joined', lookup_expr='date')
    class Meta:
        model = Teacher
        fields = ['status', 'gender', 'experience_years', 'date_joined']
