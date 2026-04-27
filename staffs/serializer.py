from rest_framework import serializers
from rest_framework.validators import UniqueValidator
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

class TeacherMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = ['id', 'first_name', 'last_name', 'employee_code', 'email_institutional']

class TeacherNameSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Teacher
        fields = ['id', 'first_name', 'last_name']

class QualificationModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Qualification
        fields = '__all__'

class UserQualificationModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserQualification
        fields = '__all__'

class SpecializationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Specialization
        fields = '__all__'

class UserSpecializationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserSpecialization
        fields = '__all__'

class DepartmentModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Department
        fields = '__all__'

class UserDepartmentModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDepartment
        fields = '__all__'

class DesignationModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Designation
        fields = '__all__'

class UserDesignationModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.UserDesignation
        fields = '__all__'
