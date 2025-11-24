from rest_framework import serializers
from staffs import models

class TeacherModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class QualificationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Qualification
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class UserQualificationModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserQualification
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Specialization
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class UserSpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserSpecialization
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class DepartmentModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
