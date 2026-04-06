from datetime import date
from django.db import transaction
from rest_framework import serializers
from courses.serializer import CourseSerializer, CourseMinimalSerializer
from utility.models import User
from students import models
from utility.serializer import BaseSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class StudentSerializer(BaseSerializer):
    user = UserSerializer()
    age = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = '__all__'

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        student = models.Student.objects.create(**validated_data, user=user)
        return student
    
    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user = instance.user
            user.username = user_data.get('username', user.username)
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()
        return super().update(instance, validated_data)

    def __init__(self, *args, **kwargs):
        allowed_list = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        include_courses = (allowed_list and 'courses' in allowed_list) or (request and request.query_params.get('courses'))

        if include_courses:
            if allowed_list and 'courses' in allowed_list:
                self.fields['courses'] = CourseMinimalSerializer(many=True, read_only=True)
            else:
                self.fields['courses'] = CourseSerializer(many=True, read_only=True)
        else:
            self.fields.pop('courses', None)

        if allowed_list is not None:
            allowed = set(allowed_list)
            existing = set(self.fields.keys())
            for field in existing - allowed:
                self.fields.pop(field)
    def get_age(self, instance):
        if instance.date_of_birth is None:
            return None
        return date.today().year - instance.date_of_birth.year

class StudentEnrollmentModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Enrollment
        fields = '__all__'


