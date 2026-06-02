from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from utility.views import Pagination20, Pagination30, Pagination100, StatusManagerMixin
from assessments import models, serializer

class ExamViewSet(StatusManagerMixin, viewsets.ModelViewSet):
    queryset = models.Exams.objects.all()
    pagination_class = Pagination20
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['course', 'start_time', 'end_time']
    search_fields = ['title', 'description']
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializer.ExamNestedSerializer
        return serializer.ExamsSerializer

class QuestionViewSet(StatusManagerMixin, viewsets.ModelViewSet):
    queryset = models.ExamQuestions.objects.all()
    serializer_class = serializer.ExamQuestionSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'question_type']
    search_fields = ['question_text']

class QuestionOptionViewSet(StatusManagerMixin, viewsets.ModelViewSet):
    queryset = models.QuestionOptions.objects.all()
    serializer_class = serializer.QuestionOptionsSerializer
    pagination_class = Pagination100
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question', 'is_correct']
