from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from assessments.models import Assignment
from courses.models import Course, Material
from staffs import models
from utility.serializer import BaseSerializer

class MappingReactivationMixin:
    """
    Mixin to provide shared validation logic for staff mapping models.
    Ensures parents are active and prevents duplicate active mappings.
    """
    def validate_mapping(self, attrs, model, target_field, target_model, target_name):
        # Handles both POST (in attrs) and PATCH (on instance)
        instance = self.instance if self.instance else None
        user = attrs.get('user', getattr(instance, 'user', None) if instance else None)
        target_obj = attrs.get(target_field, getattr(instance, target_field, None) if instance else None)
        new_status = attrs.get('status', getattr(instance, 'status', 'a') if instance else 'a')

        # Only validate when activating or creating (status != 'i')
        if new_status != 'i' and user and target_obj:
            
            # Parent Teacher check
            if not models.Teacher.objects.filter(user=user).exists():
                raise serializers.ValidationError({
                    "user": "This user is not registered as an active teacher profile."
                })
                
            # Target Entity check (Department/Qualification/etc)
            if not target_model.objects.filter(pk=target_obj.pk).exists():
                raise serializers.ValidationError({
                    target_field: f"Cannot assign to an inactive {target_name}."
                })

            # 3. Duplicate check (Excluding current instance)
            filter_kwargs = {'user': user, target_field: target_obj}
            qs = model.objects.filter(**filter_kwargs).exclude(status='i')
            if instance:
                qs = qs.exclude(pk=instance.pk)
            
            if qs.exists():
                raise serializers.ValidationError({
                    "non_field_errors": [f"This user already has an active mapping for this {target_name}."]
                })
                
        return attrs

class TeacherSerializer(BaseSerializer):
    employee_code = serializers.CharField(
        validators=[UniqueValidator(
            queryset=models.Teacher.objects.exclude(status='i'), 
            message="teacher with this employee code already exists."
        )]
    )

    email_institutional = serializers.CharField(
        validators=[UniqueValidator(
            queryset=models.Teacher.objects.exclude(status='i'), 
            message="teacher with this email institutional already exists."
        )]
    )

    def validate(self, attrs):
        current_status = self.instance.status if self.instance else 'a'
        new_status = attrs.get('status', current_status)

        if new_status == 'i':
            return attrs

        unique_fields = {
            'employee_code': "teacher with this employee code already exists.",
            'email_institutional': "teacher with this email institutional already exists.",
            'user': "An active teacher profile already exists for this user."
        }

        base_qs = models.Teacher.objects.exclude(status='i')
        if self.instance:
            base_qs = base_qs.exclude(pk=self.instance.pk)

        errors = {}
        for field, error_msg in unique_fields.items():
            val = attrs.get(field, getattr(self.instance, field, None) if self.instance else None)
            if val and base_qs.filter(**{field: val}).exists():
                errors[field] = error_msg
                
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

# --- Nested & Identity Serializers ---

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

# ADDED BACK: TeacherNameSerializer (Required by assessments app)
class TeacherNameSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = ['id', 'first_name', 'last_name']

# --- Mapping Serializers (Clean & Non-Hardcoded) ---

class QualificationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Qualification
        fields = '__all__'

class UserQualificationSerializer(MappingReactivationMixin, BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserQualification
        fields = '__all__'

    def validate(self, attrs):
        return self.validate_mapping(
            attrs, 
            model=models.UserQualification, 
            target_field='qualification', 
            target_model=models.Qualification, 
            target_name='qualification'
        )

class SpecializationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Specialization
        fields = '__all__'

class UserSpecializationSerializer(MappingReactivationMixin, BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserSpecialization
        fields = '__all__'

    def validate(self, attrs):
        return self.validate_mapping(
            attrs, 
            model=models.UserSpecialization, 
            target_field='specialization', 
            target_model=models.Specialization, 
            target_name='specialization'
        )

class DepartmentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Department
        fields = '__all__'

class UserDepartmentSerializer(MappingReactivationMixin, BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDepartment
        fields = '__all__'

    def validate(self, attrs):
        return self.validate_mapping(
            attrs, 
            model=models.UserDepartment, 
            target_field='department', 
            target_model=models.Department, 
            target_name='department'
        )

class DesignationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Designation
        fields = '__all__'

class UserDesignationSerializer(MappingReactivationMixin, BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDesignation
        fields = '__all__'

    def validate(self, attrs):
        return self.validate_mapping(
            attrs, 
            model=models.UserDesignation, 
            target_field='designation', 
            target_model=models.Designation, 
            target_name='designation'
        )
