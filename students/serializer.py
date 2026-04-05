from datetime import date
from rest_framework import serializers
from courses.serializer import CourseSerializer
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

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data.pop('user'))
        student = models.Student.objects.create(**validated_data, user=user)
        return student
    def __init__(self, *args, **kwargs):
        allowed_list = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        include_courses = (allowed_list and 'courses' in allowed_list) or (request and request.query_params.get('courses'))

        if include_courses:
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


