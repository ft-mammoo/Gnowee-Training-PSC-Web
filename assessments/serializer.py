from datetime import timedelta
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

class QuestionCategorySerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.QuestionCategories
        fields = ['id', 'name', 'description']

class ExamsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Exams
        fields = '__all__'

class QuestionOptionsSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.QuestionOptions
        fields = ['id', 'option_code', 'option_text', 'is_correct']

class ExamQuestionSerializer(BaseSerializer):
    # 'related_name="options"' in models.py will automatically fetch all linked options for this question.
    options = QuestionOptionsSerializer(many=True, read_only=True)
    category = QuestionCategorySerializer(read_only=True)

    class Meta(BaseSerializer.Meta):
        model = models.ExamQuestions
        fields = ['id', 'category', 'question_text', 'question_type', 'marks', 'options']

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
    question_count = serializers.IntegerField(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta(BaseSerializer.Meta):
        model = models.Exams
        fields = ['id', 'title', 'description', 'duration', 'start_time', 'end_time', 'total_marks', 'question_count', 'questions']
    
    def get_duration(self, obj):
        if obj.start_time and obj.end_time:
            duration = obj.end_time - obj.start_time
            total_seconds = int(duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return "00:00:00"

    def get_questions(self, obj):
        # N+1 Query Prevention
        # select_related fetches the linked question and its category in the same SQL join.
        # prefetch_related fetches all the options for those questions in one bulk query.
        mappings = obj.exam_questions.filter(
            status='a'
        ).select_related(
            'question', 'question__category'
        ).prefetch_related(
            'question__options'
        )
        
        # Extract the actual active question objects from the mapping records
        questions = [mapping.question for mapping in mappings if mapping.question.status == 'a']
        
        # Pass the extracted questions into the foundation serializer we built in Step 4
        return ExamQuestionSerializer(questions, many=True).data
