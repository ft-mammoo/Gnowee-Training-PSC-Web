import django_filters
from rest_framework.decorators import api_view, action
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status
from courses import models, serializer
from students.models import Student
from students.serializer import StudentSerializer
from utility.views import BaseViewPagination

# Function-based views for Course model
@api_view(["GET", "POST"])
def course_view(req):
    if req.method == "GET":
        qs = models.Course.objects.all()
        se = serializer.CourseSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)
    elif req.method == "POST":
        se = serializer.CourseSerializer(data=req.data)
        if not se.is_valid():
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
        se.save()
        return Response(data=se.data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PUT", "PATCH", "DELETE"])
def course_detail_view(req, pk):
    if req.method == "GET":
        try:
            course = models.Course.objects.get(pk=pk)
            se = serializer.CourseSerializer(course)
            return Response(data=se.data, status=status.HTTP_200_OK)
        except models.Course.DoesNotExist:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    elif req.method == "PUT":
        try:
            course = models.Course.objects.get(pk=pk)
            se = serializer.CourseSerializer(course, data=req.data)
            if not se.is_valid():
                return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
            se.save()
            return Response(data=se.data, status=status.HTTP_200_OK)
        except models.Course.DoesNotExist:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    elif req.method == "PATCH":
        try:
            course = models.Course.objects.get(pk=pk)
            se = serializer.CourseSerializer(course, data=req.data, partial=True)
            if not se.is_valid():
                return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
            se.save()
            return Response(data=se.data, status=status.HTTP_200_OK)
        except models.Course.DoesNotExist:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    elif req.method == "DELETE":
        try:
            course = models.Course.objects.get(pk=pk)
            course.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except models.Course.DoesNotExist:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        
@api_view(["GET"])
def course_actions_view(req, pk, action):
    if action == "students":
        qs = Student.objects.filter(courses__id=pk)
        se = StudentSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)

# Class-based views for Course model
class CourseView(APIView):
    def get(self, req):
        qs = models.Course.objects.all()
        se = serializer.CourseSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)

    def post(self, req):
        se = serializer.CourseSerializer(data=req.data)
        if not se.is_valid():
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
        se.save()
        return Response(data=se.data, status=status.HTTP_201_CREATED)
class CourseDetailedView(APIView):
    def get_object(self, pk):
        try:
            return models.Course.objects.get(pk=pk)
        except models.Course.DoesNotExist:
            return None

    def get(self, req, pk):
        course = self.get_object(pk)
        if not course:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        se = serializer.CourseSerializer(course)
        return Response(data=se.data, status=status.HTTP_200_OK)

    def put(self, req, pk):
        course = self.get_object(pk)
        if not course:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        se = serializer.CourseSerializer(course, data=req.data)
        if not se.is_valid():
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
        se.save()
        return Response(data=se.data, status=status.HTTP_200_OK)

    def patch(self, req, pk):
        course = self.get_object(pk)
        if not course:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        se = serializer.CourseSerializer(course, data=req.data, partial=True)
        if not se.is_valid():
            return Response(data=se.errors, status=status.HTTP_400_BAD_REQUEST)
        se.save()
        return Response(data=se.data, status=status.HTTP_200_OK)

    def delete(self, req, pk):
        course = self.get_object(pk)
        if not course:
            return Response(data={"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        course.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class CourseActionsView(APIView):
    def get(self, req, pk, action):
        if action == "students":
            qs = Student.objects.filter(courses__id=pk)
            se = StudentSerializer(qs, many=True)
            return Response(data=se.data, status=status.HTTP_200_OK)
class CourseGenericView(ListCreateAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseSerializer
class CourseDetailGenericView(RetrieveUpdateDestroyAPIView):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseSerializer
class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    description = django_filters.CharFilter(field_name="description", lookup_expr="icontains")
    class Meta:
        model = models.Course
        fields = ("id", "title", "description", "status")
class CourseViewSet(ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseSerializer
    filterset_class = CourseFilter
    pagination_class = BaseViewPagination
    @action(methods=["GET"], detail=True)
    def students(self, req, pk):
        qs = Student.objects.filter(enrollments__course__id=pk)
        se = StudentSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)
class CourseMixinViewSet(ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializer.CourseSerializer
    @action(methods=["GET"], detail=True)
    def students(self, req, pk):
        qs = Student.objects.filter(enrollments__course__id=pk)
        se = StudentSerializer(qs, many=True)
        return Response(data=se.data, status=status.HTTP_200_OK)

