from datetime import date
from rest_framework import serializers
from courses.serializer import CourseSerializer
from utility.models import User
from students import models
from utility.serializer import BaseSerializer

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
