from rest_framework import serializers
from utility.models import User
from students import models

class StudentSerializer(serializers.Serializer):
    GENDER_CHOICES = (
        ('m', 'Male'),
        ('f', 'Female'),
        ('o', 'Other'),
    )
    STATUS_CHOICES = (
        ('a', 'Active'),
        ('i', 'Inactive'),
        ('s', 'Suspended'),
        ('g', 'Graduated'),
        ('w', 'Withdrawn'),
    )
    id = serializers.IntegerField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())  
    first_name = serializers.CharField(max_length=100) 
    last_name = serializers.CharField(max_length=100)
    date_of_birth = serializers.DateField(required = False, allow_null=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES)
    contact_number = serializers.CharField(max_length=10)
    emergency_contact_name = serializers.CharField(max_length=100)
    emergency_contact_number = serializers.CharField(max_length=10)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, default='a')
    profile_picture = serializers.CharField(max_length=255, required = False, allow_null = True)
    date_joined = serializers.DateField()

    def create(self, validated_data):
        return models.Student.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        for k,v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance
    
    
