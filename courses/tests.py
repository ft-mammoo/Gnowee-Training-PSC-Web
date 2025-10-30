from django.test import TestCase
from django.contrib.auth import get_user_model
from courses.models import Course

User = get_user_model()

class CourseTest(TestCase):
    def setUp(self):
        # Create a test admin
        self.admin = User.objects.create_user(username='TestAdmin', password='1234')
    
    def test_signal(self):
        c1 = Course.objects.create(
            title='Physics 101',
            description='',
            status='d',
            created_by=self.admin,
            updated_by=self.admin
        )
        # Verify that the description was updated by the pre-save signal
        self.assertEqual(c1.description, "Signal Description Update")

        # Update the course to trigger post-save signal for update
        c1.title = 'Advanced Physics 101'
        c1.description = 'Advanced concepts in Physics.'
        c1.save()
