from rest_framework import serializers
from assessments import models
from staffs.serializer import TeacherNameSerializer
from utility.serializer import BaseSerializer

class AssignmentSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Assignment
        fields = '__all__'

class SubmissionSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Submission
        fields = '__all__'

class SubmissionGradeSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.SubmissionGrade
        fields = '__all__'

class QuestionCategoriesSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.QuestionCategories
        fields = '__all__'

class ExamsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Exams
        fields = '__all__'

class ExamQuestionsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamQuestions
        fields = '__all__'

class QuestionOptionsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.QuestionOptions
        fields = '__all__'

class ExamQuestionsMappingSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamQuestionsMapping
        fields = '__all__'

class ExamSubmissionsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamSubmissions
        fields = '__all__'

class ExamAnswersSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamAnswers
        fields = '__all__'

class ExamAnswerOptionsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamAnswerOptions
        fields = '__all__'

class ExamReviewsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamReviews
        fields = '__all__'


class AssignmentNestedSerializer(BaseSerializer):
    teacher = TeacherNameSerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        model = models.Assignment
        fields = ['id', 'title', 'description', 'due_date', 'teacher', 'created_date']

class ExamNestedSerializer(BaseSerializer):
    duration = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        model = models.Exams
        fields = ['id', 'title', 'description', 'duration', 'start_time', 'end_time', 'total_marks', 'question_count']
    
    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return None
    
    def get_question_count(self, obj):
        return obj.exam_questions.count()
