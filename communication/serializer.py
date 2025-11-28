from rest_framework import serializers
from communication import models

class chatSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Chat
        fields = "__all__"
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
