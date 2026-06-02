from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, mixins

from utility.views import Pagination20, Pagination30, Pagination100, StatusManagerMixin
from assessments import models, serializer

class ExamViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.Exams.objects.all().order_by('id')
    pagination_class = Pagination20
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['course', 'start_time', 'end_time']
    search_fields = ['title', 'description']
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return serializer.ExamNestedSerializer
        
        # Explicitly route the serializers for our custom action
        if self.action == 'questions':
            if self.request and self.request.method == 'POST':
                return serializer.ExamQuestionsMappingSerializer
            return serializer.ExamQuestionSerializer
            
        return serializer.ExamsSerializer

    @extend_schema(
        methods=['GET'],
        responses={200: serializer.ExamQuestionSerializer(many=True)},
        description="Get all active questions mapped to this specific exam."
    )
    @extend_schema(
        methods=['POST'],
        request=serializer.ExamQuestionsMappingSerializer,
        responses={200: serializer.ExamQuestionsMappingSerializer, 201: serializer.ExamQuestionsMappingSerializer},
        description="Map an existing question to this exam by providing the question ID."
    )
    # Block ViewSet inheritance by passing empty filter_backends and None for pagination
    @action(methods=["GET", "POST"], detail=True, pagination_class=None, filter_backends=[])
    def questions(self, request, pk=None):
        exam = get_object_or_404(self.get_queryset(), pk=pk)

        if request.method == "GET":
            # The standard .objects manager automatically excludes soft-deleted ('i') mappings.
            # We filter question__status='a' to ensure we don't fetch active mappings pointing to deleted questions.
            qs = models.ExamQuestionsMapping.objects.filter(
                exam=exam, question__status='a'
            ).select_related('question', 'question__category').order_by('id')
            
            questions = [mapping.question for mapping in qs]
            se = serializer.ExamQuestionSerializer(questions, many=True, context={'request': request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            question_id = request.data.get('question')

            if not question_id:
                return Response({"question": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
            
            # Use all_objects to check if a soft-deleted mapping already exists
            mapping = models.ExamQuestionsMapping.all_objects.filter(exam=exam, question_id=question_id).first()

            if mapping:
                if mapping.status == 'a':
                    return Response({"detail": "This question is already active in this exam."}, status=status.HTTP_400_BAD_REQUEST)
                
                # If we found a soft-deleted mapping, we reactivate it instead of creating a new one
                mapping.activate()
                se = serializer.ExamQuestionsMappingSerializer(mapping, context={'request': request})
                return Response(data=se.data, status=status.HTTP_200_OK)
            
            data = request.data.copy()
            data['exam'] = pk
            se = serializer.ExamQuestionsMappingSerializer(data=data, context={'request': request})
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamQuestionMappingViewSet(mixins.DestroyModelMixin, GenericViewSet):
    queryset = models.ExamQuestionsMapping.objects.all()
    
    def perform_destroy(self, instance):
        # This automatically sets status='i', saves, and sends the soft_deleted signal
        instance.delete()

class QuestionViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.ExamQuestions.objects.all().order_by('id')
    serializer_class = serializer.ExamQuestionSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['category', 'question_type']
    search_fields = ['question_text']


class QuestionOptionViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.QuestionOptions.objects.all().order_by('id')
    serializer_class = serializer.QuestionOptionsSerializer
    pagination_class = Pagination100
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['question', 'is_correct']

class ExamSubmissionViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.ExamSubmissions.objects.all().order_by('-id')
    serializer_class = serializer.ExamSubmissionsSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['exam', 'student']

    # We override the create method to implement the logic for reactivating 
    # a soft-deleted submission if the same student tries to start the same exam again.
    def create(self, request, *args, **kwargs):
        exam_id = request.data.get('exam')
        student_id = request.data.get('student')

        if not exam_id or not student_id:
            return Response(
                {"detail": "Both exam and student IDs are required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission = models.ExamSubmissions.all_objects.filter(
            exam_id=exam_id, student_id=student_id
        ).first()

        if submission:
            if submission.status == 'a':
                return Response(
                    {"detail": "This student has already started this exam."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Reactivate the soft-deleted submission natively
            submission.activate()
            se = self.get_serializer(submission, context={'request': request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        # Standard creation
        se = self.get_serializer(data=request.data, context={'request': request})
        if se.is_valid():
            se.save()
            return Response(data=se.data, status=status.HTTP_201_CREATED)
        return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)

class ExamAnswerViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.ExamAnswers.objects.all().order_by('-id')
    serializer_class = serializer.ExamAnswersSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['exam_submission', 'question']
