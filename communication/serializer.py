from rest_framework import serializers
from communication import models
from courses.models import Course

class chatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class chatResponseSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.all_objects.all())
    class Meta:
        model = models.ChatResponse
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
