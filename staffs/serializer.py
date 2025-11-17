from rest_framework import serializers
from staffs import models

class TeacherModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Teacher
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
