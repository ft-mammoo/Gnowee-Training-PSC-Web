from courses import models
from utility.serializer import BaseSerializer

class CourseSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Course
        fields = "__all__"

class CourseMinimalSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Course
        fields = ['id', 'title', 'status']

class CourseTeacherSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.CourseTeachers
        fields = "__all__"

class MaterialSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = models.Material
        fields = "__all__"
