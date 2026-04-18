from rest_framework import serializers
from courses import models
from utility.serializer import BaseSerializer
from staffs.serializer import TeacherMinimalSerializer, TeacherNameSerializer
from students.serializer import StudentSerializer

class CourseSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Course
        fields = "__all__"

class CourseMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Course
        fields = ['id', 'title']

class CourseTeacherSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.CourseTeachers
        fields = "__all__"

class CourseTeacherMinimalSerializer(BaseSerializer):
    teacher = TeacherMinimalSerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        model = models.CourseTeachers
        fields = ['id', 'teacher', 'status', 'created_date']

class MaterialSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Material
        fields = "__all__"

class MaterialNestedSerializer(BaseSerializer):
    teacher = TeacherNameSerializer(read_only=True)
    upload_date = serializers.DateField(source='uploaded_at', read_only=True)

    class Meta(BaseSerializer.Meta):
        model = models.Material
        fields = ['id', 'title', 'description', 'file_url', 'upload_date', 'type', 'status', 'teacher']

class StudentWithEnrollmentSerializer(StudentSerializer):
    enrollment = serializers.SerializerMethodField()

    class Meta(StudentSerializer.Meta):
        # Specific fields required by the documentation
        fields = ['id', 'first_name', 'last_name', 'contact_number', 'status', 'enrollment']

    def get_enrollment(self, obj):
        # This 'current_course_enrollment' was created by our Prefetch in the view
        enrollments = getattr(obj, 'current_course_enrollment', [])
        if enrollments:
            # Since it's a list from prefetch_related, we take the first (and only) match
            enrollment = enrollments[0]
            return {
                "id": enrollment.id,
                "enrollment_date": enrollment.enrollment_date,
                "status": enrollment.status
            }
        return None

class CourseStatsSerializer(BaseSerializer):
    total_students = serializers.IntegerField()
    active_students = serializers.IntegerField()
    total_teachers = serializers.IntegerField()
    total_materials = serializers.IntegerField()
    total_assignments = serializers.IntegerField()
    
    class Meta(BaseSerializer.Meta):
        model = models.Course
        fields = ['id', 'title', 'status', 'total_students', 'active_students', 'total_teachers', 'total_materials', 'total_assignments']
