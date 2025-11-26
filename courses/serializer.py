from rest_framework import serializers
from courses import models

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class CourseTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CourseTeachers
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Material
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
