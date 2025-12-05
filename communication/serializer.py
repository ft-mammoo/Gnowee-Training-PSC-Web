from rest_framework import serializers
from communication import models
from courses.models import Course
from utility.serializer import BaseSerializer

class chatSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Chat
        fields = "__all__"

class chatResponseSerializer(BaseSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.all_objects.all())
    class Meta(BaseSerializer.Meta):
        model = models.ChatResponse
        fields = "__all__"
