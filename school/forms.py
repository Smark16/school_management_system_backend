from django import forms
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from .models import User, Student, Teacher
from django.conf import settings

class StudentCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Student
        fields = ['name', 'reg_no', 'student_no', 'dob','year_of_enrollment', 'password']

    def clean_reg_no(self):
        reg_no = self.cleaned_data.get('reg_no')
        if User.objects.filter(username=reg_no).exists():
            raise ValidationError("A user with this registration number already exists.")
        return reg_no

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['reg_no'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['reg_no'],  # Ensure the User model has an email field if not using the reg_no as email
            is_student=True
        )
        student = super().save(commit=False)
        student.user = user
        if commit:
            student.save()
            self.send_welcome_email(student)
        return student

    def send_welcome_email(self, student):
        subject = "Welcome to the School Management System"
        message = f"Dear {student.name},\n\nWelcome to our school system. Your registration number is {student.reg_no}."
        from_email = settings.EMAIL_HOST_USER
        to_email = [student.user.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)

class TeacherCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Teacher
        fields = ['department', 'name', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            is_teacher=True
        )
        teacher = super().save(commit=False)
        teacher.user = user
        if commit:
            teacher.save()
            self.send_welcome_email(teacher)
        return teacher

    def send_welcome_email(self, teacher):
        subject = "Welcome to the School Management System"
        message = f"Dear {teacher.name},\n\nWelcome to our school system. Your email is {teacher.email}."
        from_email = settings.EMAIL_HOST_USER
        to_email = [teacher.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)
