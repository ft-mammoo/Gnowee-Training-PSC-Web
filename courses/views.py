from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from courses import models, serializer
from students.models import Student
from students.serializer import StudentModelSerializer

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
        se = StudentModelSerializer(qs, many=True)
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
            se = StudentModelSerializer(qs, many=True)
            return Response(data=se.data, status=status.HTTP_200_OK)
