import django_filters
from .models import Teacher
from assessments.models import Assignment
from courses.models import Material, Course

class TeacherFilter(django_filters.FilterSet):
    # Define filters for the Teacher model
    date_joined = django_filters.DateFilter(field_name='date_joined', lookup_expr='date')
    class Meta:
        model = Teacher
        fields = ['status', 'gender', 'experience_years', 'date_joined']

class TeacherCourseFilter(django_filters.FilterSet):
    class Meta:
        model = Course
        fields = ['status']

class TeacherMaterialFilter(django_filters.FilterSet):
    class Meta:
        model = Material
        fields = ['course', 'type', 'status']

class TeacherAssignmentFilter(django_filters.FilterSet):
    class Meta:
        model = Assignment
        fields = ['course', 'due_date']

class TeacherWorkloadFilter(django_filters.FilterSet):
    class Meta:
        model = Teacher
        fields = ['status']
