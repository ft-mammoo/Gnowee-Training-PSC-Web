from rest_framework import serializers

class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = (
            'id', 'created_date', 'updated_date', 'created_by', 'updated_by'
        )
