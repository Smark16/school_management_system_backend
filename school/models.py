from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

# Create your models here.
class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_headteacher = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Unique constraint to prevent duplicate departments
    description = models.CharField(max_length=200 ,null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True)
    term = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name
    

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # OneToOne for user profile extension
    name = models.CharField(max_length=100)  # Lowercase field names for consistency
    reg_no = models.CharField(max_length=100, unique=True)  # random number (coding is thinking channel)
    student_no = models.CharField(max_length=100, unique=True)  # Assuming Student_No is unique
    dob = models.DateField()  # Lowercase field names for consistency
    year_of_enrollment = models.PositiveIntegerField()  # More descriptive field name
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # OneToOne for user profile extension
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)  # More descriptive field name
    email = models.EmailField(max_length=100)  # Email is already unique in User model, no need to repeat here
    removed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    status = models.CharField(max_length=100, default='is_teacher')

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created and instance.is_teacher:
        TeacherProfile.objects.create(
            user=instance,
            email=instance.email
        )

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'teacherprofile'):
        instance.teacherprofile.save()


class Question(models.Model):
    text = models.TextField()
    option_1 = models.CharField(max_length=255, blank=True, null=True)
    option_2 = models.CharField(max_length=255, blank=True, null=True)
    option_3 = models.CharField(max_length=255, blank=True, null=True)
    option_4 = models.CharField(max_length=255, blank=True, null=True)
    option_5 = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to='question_images/', blank=True, null=True)
    ans = models.CharField(max_length=200, null=True, blank=True)
    answer_mode = models.CharField(max_length=10, choices=[('single', 'Single'), ('multiple', 'Multiple')], default='single')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    used_in_exam = models.BooleanField(default=False) 

    def __str__(self):
        return self.text


class Exam(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    questions = models.ManyToManyField(Question) 
    description = models.TextField(max_length=300, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='questions')  
    duration = models.DurationField()
    date = models.DateField()  # More concise field name
    status = models.CharField(max_length=100, default='No Submission')
    submission_Time = models.DateTimeField(auto_now=True)
    week = models.PositiveIntegerField(null=True, blank=True)
    current_year = models.PositiveIntegerField(default=datetime.now().year)  # Capture current year
    SessionChoices = (
        ('Beginning Term', 'Beginning Term'),
        ('Mid-Term', 'Mid-Term'),
        ('End-Term', 'End-Term')
    )
    examSession = models.CharField(choices=SessionChoices, max_length=100)

    def __str__(self):
        return self.name
    

    @staticmethod #stitic coz doesnot depend on any instance
    def get_current_term():
        current_month = datetime.now().month
        if 1 <= current_month <= 4:
            return 'Term 1'
        elif 5 <= current_month <= 8:
            return 'Term 2'
        else:
            return 'Term 3'

class FileUpload(models.Model):
    name = models.FileField(null=True, blank=True, upload_to='events/')
      
class CourseWork(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    file = models.ForeignKey(FileUpload, null=True, blank=True, on_delete=models.CASCADE)
    uploaded_at = models.DateField(auto_now_add=True)
    week = models.PositiveIntegerField()
    

class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  # More descriptive field name
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    feedback = models.CharField(max_length=200, blank=True)  # Allow blank feedback
     
    class Meta:
        ordering = ['-marks']

    def __str__(self):
        return f"{self.student.name} - {self.exam.name}"

class session(models.Model):
    SessionChoices = (
        ('Beginning Term', 'Beginning Term'),
        ('Mid-Term', 'Mid-Term'),
        ('End-Term', 'End-Term')
    ) 
    name = models.CharField(choices=SessionChoices, max_length=100)
    year = models.PositiveIntegerField(default=datetime.now().year)

    @staticmethod #stitic coz doesnot depend on any instance
    def get_current_term():
        current_month = datetime.now().month
        if 1 <= current_month <= 4:
            return 'Term 1'
        elif 5 <= current_month <= 8:
            return 'Term 2'
        else:
            return 'Term 3'

   
class Faqs(models.Model):
    question = models.CharField(max_length=200)
    answer = models.CharField(max_length=400)


class UpcomingEvents(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, null=True, blank=True)
    startDate = models.DateField(null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    files = models.ForeignKey(FileUpload, null=True, blank=True, on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='events/')
    location = models.CharField(max_length=100, null=True, blank=True)
