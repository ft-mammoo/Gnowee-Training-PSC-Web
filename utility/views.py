from rest_framework.pagination import PageNumberPagination


class BaseViewPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = None


class EnrollmentViewPagination(BaseViewPagination):
    page_size = 50


class StudentsAssignmentPagination(BaseViewPagination):
    page_size = 15


class StudentsExamsPagination(BaseViewPagination):
    page_size = 10


class CourseStudentsPagination(BaseViewPagination):
    page_size = 30


class CourseStatsPagination(BaseViewPagination):
    page_size = 15


class MaterialPagination(BaseViewPagination):
    page_size = 30


class CourseTeachersPagination(BaseViewPagination):
    page_size = 50


class TeacherPagination(BaseViewPagination):
    page_size = 20


class TeacherMaterialPagination(BaseViewPagination):
    page_size = 25


class DepartmentPagination(BaseViewPagination):
    page_size = 30


class QualificationPagination(BaseViewPagination):
    page_size = 20


class UserQualificationPagination(BaseViewPagination):
    page_size = 50


class SpecializationPagination(BaseViewPagination):
    page_size = 20


class UserSpecializationPagination(BaseViewPagination):
    page_size = 50


class DesignationPagination(BaseViewPagination):
    page_size = 20


class UserDesignationPagination(BaseViewPagination):
    page_size = 50


class Pagination20(BaseViewPagination):
    page_size = 20


class Pagination25(PageNumberPagination):
    page_size = 25


class Pagination30(BaseViewPagination):
    page_size = 30


class Pagination50(PageNumberPagination):
    page_size = 50


class Pagination100(BaseViewPagination):
    page_size = 100


class StatusManagerMixin:
    # This mixin allows ViewSets to dynamically switch between the default manager
    # and a custom 'all_objects' manager based on a 'status' query parameter.
    def get_status_manager(self, model):
        """
        Dynamically resolves the manager based on ViewSet configuration.
        """
        status_val = self.request.query_params.get("status")

        # We look for a list of 'list_actions' defined on the ViewSet.
        # If not defined, we default to only the standard 'list' action.
        allow_status_on = getattr(self, "allow_status_on", ["list"])

        if status_val and self.action in allow_status_on:
            return model.all_objects
        return model.objects

    # Override get_queryset to use the dynamic manager
    def get_queryset(self):
        """Returns the raw, unoptimized queryset from the correct manager."""
        model = self.queryset.model
        manager = self.get_status_manager(model)
        return manager.all()
