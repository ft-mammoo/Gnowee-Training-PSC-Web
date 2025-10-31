from django.db import models
from django.contrib.auth import get_user_model
from utility.models import BaseModel, SoftDeleteModel

User = get_user_model()

class Assignment(SoftDeleteModel):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    teacher = models.ForeignKey('staffs.Teacher', on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - (Course_ID:{self.course_id})"
    

#Submition of assignment by students
class Submission(SoftDeleteModel):
    STATUS_CHOICES = [
        ("s", "Submitted"),
        ("l", "Late"),
        ("g", "Graded"),
    ]
    assignment = models.ForeignKey('Assignment', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    file_url = models.CharField(max_length=255)
    submitted_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="s")

    def __str__(self):
        return f"Submission {self.id}: Assignment {self.assignment_id} by Student {self.student_id}"
    
#Grading of assignment by teacher
class SubmissionGrade(SoftDeleteModel):
    submission = models.ForeignKey('Submission', on_delete=models.CASCADE)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    graded_by = models.ForeignKey('staffs.Teacher', on_delete=models.DO_NOTHING, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Grading {self.id}: Grade {self.grade} for Submission {self.submission_id} by Teacher {self.graded_by_id}"

class QuestionCategories(SoftDeleteModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class Exams(SoftDeleteModel):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_marks = models.IntegerField()

    def __str__(self):
        return f"{self.title} - (Course_ID:{self.course_id})"

class ExamQuestions(SoftDeleteModel):
    QUESTION_TYPE_CHOICES = (
        ('s', 'Single'),
        ('m', 'Multiple'),
        ('t', 'Text'),
    )
    category = models.ForeignKey('QuestionCategories', on_delete=models.SET_NULL, null=True, blank=True)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    marks = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"Question {self.id} for Exam {self.exam_id}"
    
class QuestionOptions(SoftDeleteModel):
    question = models.ForeignKey('ExamQuestions', on_delete=models.CASCADE, related_name='options')
    option_code = models.CharField(max_length=4)
    option_text = models.TextField()
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Option {self.option_code} for Question {self.question_id}"

class ExamQuestionsMapping(SoftDeleteModel):
    exam = models.ForeignKey('Exams', on_delete=models.CASCADE, related_name='exam_questions')
    question = models.ForeignKey('ExamQuestions', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('exam', 'question')

    def __str__(self):
        return f"Exam {self.exam_id} - Question {self.question_id}"

class ExamSubmissions(SoftDeleteModel):
    exam = models.ForeignKey('Exams', on_delete=models.CASCADE)
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE)
    submission_time = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('exam', 'student')

    def __str__(self):
        return f"Exam Submission {self.id}: Exam {self.exam_id} by Student {self.student_id}"

class ExamAnswers(SoftDeleteModel):
    exam_submission = models.ForeignKey('ExamSubmissions', on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('ExamQuestions', on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Answer {self.id}: Exam {self.exam_id} by Student {self.student_id} for Question {self.question_id}"

class ExamAnswerOptions(SoftDeleteModel):
    answer = models.ForeignKey('ExamAnswers', on_delete=models.CASCADE)
    option = models.ForeignKey('QuestionOptions', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('answer', 'option')

    def __str__(self):
        return f"Selected Option {self.option_id} for Answer {self.exam_answer_id}"

class ExamReviews(SoftDeleteModel):
    exam_submission = models.ForeignKey('ExamSubmissions', on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    graded_by = models.ForeignKey('staffs.Teacher', on_delete=models.DO_NOTHING)
    feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Review {self.id}: Exam Submission {self.exam_submission_id} reviewed by Teacher {self.reviewed_by_id}"
