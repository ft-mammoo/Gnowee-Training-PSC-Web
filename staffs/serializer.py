from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from assessments.models import Assignment
from courses.models import Course, Material
from staffs import models
from utility.serializer import BaseSerializer

class TeacherSerializer(BaseSerializer):

    employee_code = serializers.CharField(
        validators=[UniqueValidator(
            # Exclude inactive teachers from the uniqueness check
            queryset=models.Teacher.objects.exclude(status='i'), 
            message="teacher with this employee code already exists."
        )]
    )

    email_institutional = serializers.CharField(
        validators=[UniqueValidator(
            # Exclude inactive teachers from the uniqueness check
            queryset=models.Teacher.objects.exclude(status='i'), 
            message="teacher with this email institutional already exists."
        )]
    )

    # Custom validation to catch uniqueness violations during partial updates (PATCH) where unique fields are omitted but status changes to active.
    def validate(self, attrs):
        current_status = self.instance.status if self.instance else 'a'
        new_status = attrs.get('status', current_status)

        # If the profile is inactive, no unique checks are needed.
        if new_status == 'i':
            return attrs

        # Define the fields we need to protect and their specific error messages
        unique_fields = {
            'employee_code': "teacher with this employee code already exists.",
            'email_institutional': "teacher with this email institutional already exists.",
            'user': "An active teacher profile already exists for this user."
        }

        # Build the base queryset (Active teachers, excluding the current one)
        base_qs = models.Teacher.objects.exclude(status='i')
        if self.instance:
            base_qs = base_qs.exclude(pk=self.instance.pk)

        # Dynamically check all fields and collect all errors simultaneously
        errors = {}
        for field, error_msg in unique_fields.items():
            # Get the new value from the request, or fallback to the existing database value
            val = attrs.get(field, getattr(self.instance, field, None) if self.instance else None)
            
            # **{field: val} dynamically unpacks to e.g., employee_code="EMP001"
            if val and base_qs.filter(**{field: val}).exists():
                errors[field] = error_msg
                
        # If we caught any collisions, raise them all at once
        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = '__all__'

        validators = [
            serializers.UniqueTogetherValidator(
                queryset=models.Teacher.objects.exclude(status='i'),
                fields=['user'],
                message="An active teacher profile already exists for this user."
            )
        ]

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
    
    # active qualification validation
    def validate_qualification(self, value):
        if value.status != 'a':
            raise serializers.ValidationError("Cannot assign to an inactive qualification.")
        return value

    # unique validation
    def validate(self, attrs):
        user = attrs.get('user', getattr(self.instance, 'user', None))
        qualification = attrs.get('qualification', getattr(self.instance, 'qualification', None))
        new_status = attrs.get('status', getattr(self.instance, 'status', 'a'))

        if new_status != 'i' and user and qualification:
            # Let the default manager determine if the teacher is active
            if not models.Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError("Cannot activate: The associated teacher profile is inactive.")
                
            # Let the default manager determine if the qualification is active
            if not models.Qualification.objects.filter(pk=qualification.pk).exists():
                raise serializers.ValidationError("Cannot activate: The associated qualification is inactive.")

            # Check for active duplicates (excluding self)
            qs = models.UserQualification.objects.filter(user=user, qualification=qualification).exclude(status='i')
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This user already has an active mapping for this qualification.")
        return attrs

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
    
    # active specialization validation
    def validate_specialization(self, value):
        if value.status != 'a':
            raise serializers.ValidationError("Cannot assign to an inactive specialization.")
        return value

    # unique validation
    def validate(self, attrs):
        user = attrs.get('user', getattr(self.instance, 'user', None))
        specialization = attrs.get('specialization', getattr(self.instance, 'specialization', None))
        new_status = attrs.get('status', getattr(self.instance, 'status', 'a'))

        if new_status != 'i' and user and specialization:
            # Let the default manager determine if the teacher is active
            if not models.Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError("Cannot activate: The associated teacher profile is inactive.")
                
            # Let the default manager determine if the specialization is active
            if not models.Specialization.objects.filter(pk=specialization.pk).exists():
                raise serializers.ValidationError("Cannot activate: The associated specialization is inactive.")

            # Check for active duplicates (excluding self)
            qs = models.UserSpecialization.objects.filter(user=user, specialization=specialization).exclude(status='i')
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This user already has an active mapping for this specialization.")
        return attrs

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
    
    # active department validation
    def validate_department(self, value):
        if value.status != 'a':
            raise serializers.ValidationError("Cannot assign to an inactive department.")
        return value

    # unique validation
    def validate(self, attrs):
        user = attrs.get('user', getattr(self.instance, 'user', None))
        department = attrs.get('department', getattr(self.instance, 'department', None))
        new_status = attrs.get('status', getattr(self.instance, 'status', 'a'))

        if new_status != 'i' and user and department:
            # Let the default manager determine if the teacher is active
            if not models.Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError("Cannot activate: The associated teacher profile is inactive.")
                
            # Let the default manager determine if the department is active
            if not models.Department.objects.filter(pk=department.pk).exists():
                raise serializers.ValidationError("Cannot activate: The associated department is inactive.")

            # Check for active duplicates (excluding self)
            qs = models.UserDepartment.objects.filter(user=user, department=department).exclude(status='i')
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This user already has an active mapping for this department.")
        return attrs

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
    
    # active designation validation
    def validate_designation(self, value):
        if value.status != 'a':
            raise serializers.ValidationError("Cannot assign to an inactive designation.")
        return value
    
    # unique validation
    def validate(self, attrs):
        user = attrs.get('user', getattr(self.instance, 'user', None))
        designation = attrs.get('designation', getattr(self.instance, 'designation', None))
        new_status = attrs.get('status', getattr(self.instance, 'status', 'a'))

        if new_status != 'i' and user and designation:
            # Let the default manager determine if the teacher is active
            if not models.Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError("Cannot activate: The associated teacher profile is inactive.")
                
            # Let the default manager determine if the designation is active
            if not models.Designation.objects.filter(pk=designation.pk).exists():
                raise serializers.ValidationError("Cannot activate: The associated designation is inactive.")

            # Check for active duplicates (excluding self)
            qs = models.UserDesignation.objects.filter(user=user, designation=designation).exclude(status='i')
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError("This user already has an active mapping for this designation.")
        return attrs
