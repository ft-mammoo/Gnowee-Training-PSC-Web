from datetime import date
from rest_framework import serializers
from courses.serializer import CourseSerializer
from utility.models import User
from students import models
from utility.serializer import BaseSerializer

class StudentModelSerializer(BaseSerializer):
    age = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = '__all__'
    
    def get_age(self, instance):
        return date.today().year - instance.date_of_birth.year
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class StudentNestedSerializer(BaseSerializer):
    user = UserSerializer()
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        student = models.Student.objects.create(user=user, **validated_data)
        return student
    
class StudentAndCourseNestedSerializer(BaseSerializer):
    user = UserSerializer()
    courses = CourseSerializer(read_only=True, many=True)
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = "__all__"

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        student = models.Student.objects.create(user=user, **validated_data)
        return student
    

class StudentEnrollmentModelSerializer(BaseSerializer):
    
    class Meta(BaseSerializer.Meta):
        model = models.Enrollment
        fields = '__all__'
