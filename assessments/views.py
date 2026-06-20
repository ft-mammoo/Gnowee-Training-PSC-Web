from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from assessments import filters, models, serializer
from utility.views import Pagination20, Pagination25, Pagination30, Pagination50, Pagination100, StatusManagerMixin


class ExamViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.Exams.objects.all().order_by("id")
    pagination_class = Pagination20
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["course", "start_time", "end_time"]
    search_fields = ["title", "description"]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return serializer.ExamNestedSerializer

        # Explicitly route the serializers for our custom action
        if self.action == "questions":
            if self.request and self.request.method == "POST":
                return serializer.ExamQuestionsMappingSerializer
            return serializer.ExamQuestionSerializer

        return serializer.ExamsSerializer

    @extend_schema(
        methods=["GET"],
        responses={200: serializer.ExamQuestionSerializer(many=True)},
        description="Get all active questions mapped to this specific exam.",
    )
    @extend_schema(
        methods=["POST"],
        request=serializer.ExamQuestionsMappingSerializer,
        responses={
            200: serializer.ExamQuestionsMappingSerializer,
            201: serializer.ExamQuestionsMappingSerializer,
        },
        description="Map an existing question to this exam by providing the question ID.",
    )
    # Block ViewSet inheritance by passing empty filter_backends and None for pagination
    @action(methods=["GET", "POST"], detail=True, pagination_class=None, filter_backends=[])
    def questions(self, request, pk=None):
        exam = get_object_or_404(self.get_queryset(), pk=pk)

        if request.method == "GET":
            # The standard .objects manager automatically excludes soft-deleted ('i') mappings.
            # We filter question__status='a' to ensure we don't fetch active mappings pointing to deleted questions.
            qs = (
                models.ExamQuestionsMapping.objects.filter(exam=exam, question__status="a")
                .select_related("question", "question__category")
                .order_by("id")
            )

            questions = [mapping.question for mapping in qs]
            se = serializer.ExamQuestionSerializer(questions, many=True, context={"request": request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        elif request.method == "POST":
            question_id = request.data.get("question")

            if not question_id:
                return Response(
                    {"question": ["This field is required."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use all_objects to check if a soft-deleted mapping already exists
            mapping = models.ExamQuestionsMapping.all_objects.filter(exam=exam, question_id=question_id).first()

            if mapping:
                if mapping.status == "a":
                    return Response(
                        {"detail": "This question is already active in this exam."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # If we found a soft-deleted mapping, we reactivate it instead of creating a new one
                mapping.activate()
                se = serializer.ExamQuestionsMappingSerializer(mapping, context={"request": request})
                return Response(data=se.data, status=status.HTTP_200_OK)

            data = request.data.copy()
            data["exam"] = pk
            se = serializer.ExamQuestionsMappingSerializer(data=data, context={"request": request})
            if se.is_valid():
                se.save()
                return Response(data=se.data, status=status.HTTP_201_CREATED)
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        methods=["DELETE"],
        responses={204: None},
        description="Remove a question from an exam (soft delete the mapping).",
    )
    @action(
        methods=["DELETE"],
        detail=True,
        url_path=r"questions/(?P<question_id>\d+)",
        filter_backends=[],
        pagination_class=None,
    )
    def remove_question(self, request, pk=None, question_id=None):
        exam = get_object_or_404(self.get_queryset(), pk=pk)

        # Look up the active mapping
        mapping = models.ExamQuestionsMapping.objects.filter(exam=exam, question_id=question_id, status="a").first()

        if not mapping:
            return Response(
                {"detail": "Active mapping not found for this exam and question."}, status=status.HTTP_404_NOT_FOUND
            )

        # Execute soft-delete
        mapping.status = "i"
        mapping.save(update_fields=["status"])

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        responses={200: serializer.ExamSubmissionsSerializer(many=True)},
        description="Get all submissions for a specific exam.",
    )
    @action(methods=["GET"], detail=True, pagination_class=Pagination30)
    def submissions(self, request, pk=None):
        exam = get_object_or_404(self.get_queryset(), pk=pk)

        # Base query optimized to prevent N+1 lookup on the nested student/user data
        qs = (
            models.ExamSubmissions.objects.filter(exam=exam, status="a")
            .select_related("student__user")
            .order_by("-id")
        )

        # Custom filtering mapped from API spec requirements
        student_id = request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)

        submission_time = request.query_params.get("submission_time")
        if submission_time:
            # Casts the datetime field to a date for clean string matching (YYYY-MM-DD)
            qs = qs.filter(submission_time__date=submission_time)

        page = self.paginate_queryset(qs)
        if page is not None:
            se = serializer.ExamSubmissionsSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(se.data)

        se = serializer.ExamSubmissionsSerializer(qs, many=True, context={"request": request})
        return Response(data=se.data, status=status.HTTP_200_OK)


class QuestionViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.ExamQuestions.objects.select_related("category").prefetch_related("options").all().order_by("id")
    serializer_class = serializer.ExamQuestionSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["category", "question_type"]
    search_fields = ["question_text"]


class QuestionOptionViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.QuestionOptions.objects.all().order_by("id")
    serializer_class = serializer.QuestionOptionsSerializer
    pagination_class = Pagination100
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["question", "is_correct"]


class ExamSubmissionViewSet(
    StatusManagerMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, GenericViewSet
):
    """
    Restricted to List, Retrieve, and Create operations only.
    No updates or deletes allowed on submissions via the API.
    """

    queryset = models.ExamSubmissions.objects.all()
    serializer_class = serializer.ExamSubmissionsSerializer
    pagination_class = Pagination30
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["exam", "student"]

    def get_queryset(self):
        qs = super().get_queryset()
        # Optimized with select_related to prevent N+1 on nested exam/student reads
        return qs.select_related("exam", "student__user").order_by("-id")

    """
    We override the create method to implement the logic for reactivating
    a soft-deleted submission if the same student tries to start the same exam again.
    """

    def create(self, request, *args, **kwargs):
        exam_id = request.data.get("exam")
        student_id = request.data.get("student")

        if not exam_id or not student_id:
            return Response(
                {"detail": "Both exam and student IDs are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        submission = models.ExamSubmissions.all_objects.filter(exam_id=exam_id, student_id=student_id).first()

        if submission:
            if submission.status == "a":
                return Response(
                    {"detail": "This student has already started this exam."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # Reactivate the soft-deleted submission natively
            submission.activate()
            se = self.get_serializer(submission, context={"request": request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        # Standard creation
        se = self.get_serializer(data=request.data, context={"request": request})
        if se.is_valid():
            se.save()
            return Response(data=se.data, status=status.HTTP_201_CREATED)

        return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)


class ExamAnswerViewSet(StatusManagerMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    Restricted strictly to POST (Create) operation only.
    No listing, retrieving, updating, or deleting of answers via the API.
    """

    queryset = models.ExamAnswers.objects.all()
    serializer_class = serializer.ExamAnswersSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by("-id")


class QuestionCategoryViewSet(StatusManagerMixin, mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    Restricted strictly to GET (List) and POST (Create) operations only.
    No updates or deletes allowed on categories via the API
    """

    queryset = models.QuestionCategories.objects.all()
    serializer_class = serializer.QuestionCategorySerializer
    pagination_class = Pagination30
    filter_backends = [SearchFilter]
    search_fields = ["name"]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.order_by("-id")


class AssignmentViewSet(StatusManagerMixin, ModelViewSet):
    queryset = models.Assignment.objects.all()
    pagination_class = Pagination25
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["course", "teacher", "due_date", "created_date"]
    search_fields = ["title", "description"]

    def get_queryset(self):
        """
        1. Call super() to let the mixin evaluate ?status=i and pick the right manager.
        2. Chain select_related to prevent N+1 queries on the nested teacher data.
        """
        qs = super().get_queryset()
        return qs.select_related("teacher__user").order_by("-id")

    def get_serializer_class(self):
        # Flat writes (POST/PATCH), nested reads (GET)
        if self.action in ["list", "retrieve"]:
            return serializer.AssignmentNestedSerializer
        return serializer.AssignmentSerializer

    @extend_schema(
        responses={200: serializer.SubmissionSerializer(many=True)},
        description="Get all submissions for a specific assignment.",
    )
    @action(methods=["GET"], detail=True, pagination_class=Pagination30)
    def submissions(self, request, pk=None):
        assignment = get_object_or_404(self.get_queryset(), pk=pk)

        # Base query optimized to prevent N+1 lookup on the student data
        qs = models.Submission.objects.filter(assignment=assignment).select_related("student__user").order_by("-id")

        # Clean, explicit manual filtering for the custom action
        status_val = request.query_params.get("status")
        if status_val:
            qs = qs.filter(status=status_val)

        submitted_date = request.query_params.get("submitted_date")
        if submitted_date:
            qs = qs.filter(submitted_date__date=submitted_date)

        search_val = request.query_params.get("search")
        if search_val:
            qs = qs.filter(
                Q(student__user__first_name__icontains=search_val) | Q(student__user__last_name__icontains=search_val)
            )

        page = self.paginate_queryset(qs)
        if page is not None:
            se = serializer.SubmissionSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(se.data)

        se = serializer.SubmissionSerializer(qs, many=True, context={"request": request})
        return Response(data=se.data, status=status.HTTP_200_OK)

    @extend_schema(
        responses={200: serializer.SubmissionSerializer(many=True)},
        description="Get all pending (ungraded) submissions for a specific assignment.",
    )
    @action(methods=["GET"], detail=True, url_path="submissions/pending", pagination_class=Pagination30)
    def pending_submissions(self, request, pk=None):
        assignment = get_object_or_404(self.get_queryset(), pk=pk)

        # Filter strictly for 's' (Submitted) and 'l' (Late).
        qs = (
            models.Submission.objects.filter(assignment=assignment, status__in=["s", "l"])
            .select_related("student__user")
            .order_by("-id")
        )

        search_val = request.query_params.get("search")
        if search_val:
            qs = qs.filter(
                Q(student__user__first_name__icontains=search_val) | Q(student__user__last_name__icontains=search_val)
            )

        page = self.paginate_queryset(qs)
        if page is not None:
            se = serializer.SubmissionSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(se.data)

        se = serializer.SubmissionSerializer(qs, many=True, context={"request": request})
        return Response(data=se.data, status=status.HTTP_200_OK)


class SubmissionViewSet(StatusManagerMixin, ModelViewSet):
    """
    Standard CRUD operations for Assignment Submissions.
    Enforces deadline checks on creation and blocks updates on graded submissions.
    """

    queryset = models.Submission.objects.all()
    serializer_class = serializer.SubmissionSerializer
    pagination_class = Pagination30

    # Use the dedicated filter class instead of raw filterset_fields
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.SubmissionFilter

    def get_queryset(self):
        # Clean, optimized N+1 protection. No manual query param parsing here.
        qs = super().get_queryset()
        return qs.select_related("assignment", "student__user").order_by("-id")

    def create(self, request, *args, **kwargs):
        assignment_id = request.data.get("assignment")

        if assignment_id:
            assignment = get_object_or_404(models.Assignment, id=assignment_id)

            # Deadline enforcement.
            current_date = timezone.now().date()
            if assignment.due_date and assignment.due_date < current_date:
                return Response({"detail": "Submission deadline has passed."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent a student from altering a submission after a teacher has graded it
        if instance.status == "g":
            return Response({"detail": "Cannot update a graded submission."}, status=status.HTTP_400_BAD_REQUEST)

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Prevent a student from deleting a submission after a teacher has graded it
        if instance.status == "g":
            return Response({"detail": "Cannot delete a graded submission."}, status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


class SubmissionGradeViewSet(
    StatusManagerMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    """
    API endpoint for teachers to grade submissions.
    Restricted to GET, POST, and PATCH. Deletion is physically disabled.
    """

    queryset = models.SubmissionGrade.objects.all()
    serializer_class = serializer.SubmissionGradeSerializer
    pagination_class = Pagination50

    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.SubmissionGradeFilter

    def get_queryset(self):
        qs = super().get_queryset()
        # N+1 protection for relational teacher and submission reads
        return qs.select_related("submission", "graded_by__user").order_by("-id")

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Save the grade and explicitly transition the parent submission status to 'g' (Graded).
        Wrapped in an atomic transaction to ensure both records succeed or fail together.
        """
        # Save the new SubmissionGrade instance
        grade_instance = serializer.save()

        # Native, optimized update to the parent Submission
        submission = grade_instance.submission
        submission.status = "g"
        submission.save(update_fields=["status"])


class ExamAnswerOptionViewSet(StatusManagerMixin, mixins.CreateModelMixin, GenericViewSet):
    """
    Restricted strictly to POST (Create) operations.
    Links a selected QuestionOption to a submitted ExamAnswer.
    Engineered to handle rapid toggling by reactivating soft-deleted options
    instead of duplicating rows or hitting uniqueness constraints.
    """

    queryset = models.ExamAnswerOptions.objects.all()
    serializer_class = serializer.ExamAnswerOptionsSerializer

    def create(self, request, *args, **kwargs):
        answer_id = request.data.get("answer")
        option_id = request.data.get("option")

        if not answer_id or not option_id:
            return Response(
                {"detail": "Both answer and option IDs are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Query using all_objects to bypass the active-only default manager
        existing_option = models.ExamAnswerOptions.all_objects.filter(answer_id=answer_id, option_id=option_id).first()

        if existing_option:
            # If it's already active, block the duplicate request
            if existing_option.status == "a":
                return Response(
                    {"detail": "This option is already selected for this answer."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 2. Reactivate the soft-deleted record instead of creating a new one
            existing_option.activate()
            se = self.get_serializer(existing_option, context={"request": request})
            return Response(data=se.data, status=status.HTTP_200_OK)

        # 3. Standard creation if no record has ever existed for this pairing
        se = self.get_serializer(data=request.data, context={"request": request})
        if se.is_valid():
            se.save()
            return Response(data=se.data, status=status.HTTP_201_CREATED)

        return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
