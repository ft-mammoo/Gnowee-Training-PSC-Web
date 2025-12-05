from assessments import models
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
