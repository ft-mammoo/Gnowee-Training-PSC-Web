from assessments import models
from utility.serializer import BaseSerializer
from rest_framework import serializers

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

class GradeMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.SubmissionGrade
        fields = ['grade', 'feedback']

class SubmissionGradeMinimalSerializer(BaseSerializer):
    grade = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = models.Submission
        fields = ['id', 'status', 'submitted_date', 'grade']

    def get_grade(self, instance):
        grade = models.SubmissionGrade.objects.filter(submission=instance).first()
        if grade:
            return GradeMinimalSerializer(grade).data
        return None

class ExamReviewMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.ExamReviews
        fields = ['score', 'feedback']

class ExamSubmissionMinimalSerializer(BaseSerializer):
    submitted_at = serializers.DateTimeField(source='submission_time', read_only=True)
    review = serializers.SerializerMethodField()
    class Meta(BaseSerializer.Meta):
        model = models.ExamSubmissions
        fields = ['id', 'submitted_at', 'review']

    def get_review(self, instance):
        review = models.ExamReviews.objects.filter(exam_submission=instance).first()
        if review:
            return ExamReviewMinimalSerializer(review).data
        return None

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
