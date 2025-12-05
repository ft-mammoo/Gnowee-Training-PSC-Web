from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = (
            'id', 'created_at', 'updated_at', 'created_by', 'updated_by'
        )
