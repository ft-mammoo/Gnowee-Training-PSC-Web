from datetime import date
from rest_framework import serializers
from courses.serializer import CourseSerializer, CourseMinimalSerializer
from utility.models import User
from students import models
from utility.serializer import BaseSerializer
from courses.models import Course
from assessments.models import Assignment, Exams, Submission, ExamSubmissions
from assessments.serializer import ExamSubmissionMinimalSerializer, SubmissionGradeMinimalSerializer

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

class StudentEnrollmentMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Enrollment
        fields = ['id','enrollment_date', 'status']

class StudentWithCoursesSerializer(BaseSerializer):
    courses = CourseMinimalSerializer(read_only=True, many=True)
    class Meta(BaseSerializer.Meta):
        model = models.Student
        fields = ['id', 'first_name', 'last_name', 'status', 'courses']
class StudentCourseSerializer(BaseSerializer):
    enrollment = StudentEnrollmentMinimalSerializer(source='enrollments', many=True, read_only=True)
    class Meta(BaseSerializer.Meta):
        model = Course
        fields = ['id', 'title', 'description', 'status', 'enrollment']

class StudentAssignmentSerializer(BaseSerializer):
    course = CourseMinimalSerializer(read_only=True)
    submission = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = Assignment
        fields = ['id', 'title', 'course', 'due_date', 'submission']
    
    def get_submission(self, instance):
        student = self.context.get('student')
        if student:
            submission = Submission.objects.filter(assignment=instance, student=student).first()
            if submission:
                return SubmissionGradeMinimalSerializer(submission).data
        return None

class StudentExamSerializer(BaseSerializer):
    course = CourseMinimalSerializer(read_only=True)
    duration = serializers.SerializerMethodField()
    submission = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = Exams
        fields = ['id', 'title', 'course', 'start_time', 'end_time', 'duration', 'total_marks', 'submission']

    def get_duration(self, instance):
        if instance.start_time and instance.end_time:
            duration = instance.end_time - instance.start_time
            return str(duration)
        return None
    
    def get_submission(self, instance):
        student = self.context.get('student')
        if student:
            submission = ExamSubmissions.objects.filter(exam=instance, student=student).first()
            if submission:
                return ExamSubmissionMinimalSerializer(submission).data
        return None

