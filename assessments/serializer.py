from rest_framework import serializers
from assessments import models

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Assignment
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Submission
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SubmissionGrade
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class QuestionCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionCategories
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class ExamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Exams
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class ExamQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExamQuestions
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class QuestionOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuestionOptions
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class ExamQuestionsMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExamQuestionsMapping
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class ExamSubmissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExamSubmissions
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]

class ExamAnswersSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ExamAnswers
        fields = '__all__'
        read_only_fields = [
            'id', 'created_by', 'updated_by', 'created_date', 'updated_date'
        ]
