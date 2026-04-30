from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from assessments.models import Assignment
from courses.models import Course, Material
from staffs import models
from utility.serializer import BaseSerializer

class TeacherSerializer(BaseSerializer):

    employee_code = serializers.CharField(
        validators=[UniqueValidator(
            queryset=models.Teacher.objects.all(), 
            message="teacher with this employee code already exists."
        )]
    )

    email_institutional = serializers.CharField(
        validators=[UniqueValidator(
            queryset=models.Teacher.objects.all(), 
            message="teacher with this email institutional already exists."
        )]
    )

    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = '__all__'

class TeacherCourseListSerializer(BaseSerializer):
    assignment = serializers.SerializerMethodField()
    student_count = serializers.IntegerField(read_only=True)

    class Meta(BaseSerializer.Meta):
        model = Course
        fields = ['id', 'title', 'description', 'status', 'assignment', 'student_count']

    def get_assignment(self, obj):
        assignments = getattr(obj, 'teacher_assignments', [])
        if assignments:
            mapping = assignments[0]
            return {
                "id": mapping.id,
                "status": mapping.status,
                "created_date": mapping.created_date,
            }
        return None
    
class TeacherMaterialSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Material
        fields = '__all__'

class TeacherAssignmentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Assignment
        fields = '__all__'

class TeacherWorkloadSerializer(BaseSerializer):
    total_courses = serializers.IntegerField(read_only=True)
    total_students = serializers.IntegerField(read_only=True)
    total_assignments = serializers.IntegerField(read_only=True)
    pending_submissions = serializers.IntegerField(read_only=True)

    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = [
            'id', 'first_name', 'last_name', 'employee_code', 'status',
            'total_courses', 'total_students', 'total_assignments', 'pending_submissions'
        ]

class TeacherMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = ['id', 'first_name', 'last_name', 'employee_code', 'email_institutional']

class TeacherNameSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = ['id', 'first_name', 'last_name']

class QualificationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Qualification
        fields = '__all__'

class UserQualificationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserQualification
        fields = '__all__'
    # active teacher validation
    def validate_user(self, value):
        if not models.Teacher.objects.filter(user=value, status='a').exists():
            raise serializers.ValidationError("This user is not registered as an active teacher.")
        return value

class SpecializationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Specialization
        fields = '__all__'

class UserSpecializationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserSpecialization
        fields = '__all__'
    # active teacher validation
    def validate_user(self, value):
        if not models.Teacher.objects.filter(user=value, status='a').exists():
            raise serializers.ValidationError("This user is not registered as an active teacher.")
        return value

class DepartmentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Department
        fields = '__all__'

class UserDepartmentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDepartment
        fields = '__all__'
    # active teacher validation
    def validate_user(self, value):
        if not models.Teacher.objects.filter(user=value, status='a').exists():
            raise serializers.ValidationError("This user is not registered as an active teacher.")
        return value

class DesignationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Designation
        fields = '__all__'

class UserDesignationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDesignation
        fields = '__all__'
    # active teacher validation
    def validate_user(self, value):
        if not models.Teacher.objects.filter(user=value, status='a').exists():
            raise serializers.ValidationError("This user is not registered as an active teacher.")
        return value
