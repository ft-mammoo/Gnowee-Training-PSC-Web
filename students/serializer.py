from datetime import date
from rest_framework import serializers
from courses.serializer import CourseSerializer
from utility.models import User
from students import models
from utility.serializer import BaseSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class StudentSerializer(BaseSerializer):
    user = UserSerializer()
    age = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        student = models.Student.objects.create(user=user, **validated_data)
        return student
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None:
            if request.query_params.get('courses'):
                self.fields['courses'] = CourseSerializer(many=True)
            else:
                self.fields.pop('courses', None)
    def get_age(self, instance):
        return date.today().year - instance.date_of_birth.year

class StudentEnrollmentModelSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Enrollment
        fields = '__all__'


