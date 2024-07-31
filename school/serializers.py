from .models import *
from rest_framework import serializers
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_student', 'is_teacher']

class ObtainSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['is_student'] = user.is_student
        token['is_teacher'] = user.is_teacher
        token['is_headteacher'] = user.is_headteacher
        token['username'] = user.username
        token['email'] = user.email 

        return token

class StudentRegistration(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = Student
        fields = ['id', 'name', 'reg_no', 'student_no', 'dob', 'year_of_enrollment', 'password']

    def create(self, validated_data):
        user_data = {
            'username': validated_data['reg_no'],
            'is_student': True,
        }
        password = validated_data.pop('password')
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        student = Student.objects.create(
            user=user,
            name=validated_data['name'],
            reg_no=validated_data['reg_no'],
            student_no=validated_data['student_no'],
            dob=validated_data['dob'],
            year_of_enrollment=validated_data['year_of_enrollment']
        )
        
        # Send welcome email
        self.send_welcome_email(student)
        
        return student

    def send_welcome_email(self, student):
        subject = "Welcome to the School Management System"
        message = f"Dear {student.name},\n\nWelcome to our school system. Your registration number is {student.reg_no}."
        from_email = settings.EMAIL_HOST_USER
        to_email = [student.user.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)

class TeacherRegistration(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = Teacher
        fields = ['id', 'department', 'email', 'name', 'password']

    def create(self, validated_data):
        user_data = {
            'username': validated_data['email'],
            'is_teacher': True,
        }
        password = validated_data.pop('password')
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()

        teacher = Teacher.objects.create(
            user=user,
            name = validated_data['name'],
            department=validated_data['department'],
            email=validated_data['email']
        )
        
        # Send welcome email
        self.send_welcome_email(teacher)
        
        return teacher

    def send_welcome_email(self, teacher):
        subject = "Welcome to the School Management System"
        message = f"Dear {teacher.user.username},\n\nWelcome to our school system. Your username is {teacher.email} and password is {teacher.user.password}"
        from_email = settings.EMAIL_HOST_USER
        to_email = [teacher.email]
        send_mail(subject, message, from_email, to_email, fail_silently=False)

# change password
class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        # Check if the new password and its confirmation match
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        # Verify that the provided old password matches the user's current password
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user

        # make sure user is only able to update their own password
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You don't have permission for this user."})

        # Set the new password for the user instance
        instance.set_password(validated_data['password'])
        instance.save()

        return instance

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'reg_no', 'student_no', 'dob', 'year_of_enrollment', 'user', 'removed']

      

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class TeacherSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Teacher
        fields = ['id','user', 'name','department', 'email', 'removed']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['department'] = DepartmentSerializer(instance.department).data
        return response

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
       # fields = ['id', 'text', 'option_1', 'option_2', 'option_3', 'option_4', 'option_5', 'ans', 'teacher', 'department']

class ExamSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Exam

        fields = ['id', 'name', 'duration','description', 'date', 'week', 'current_year','examSession','status', 'submission_Time', 'get_current_term','questions','department', 'student']

    def to_representation(self, instance):
        response =  super().to_representation(instance)
        response['department'] = DepartmentSerializer(instance.department).data
        response['questions'] = QuestionSerializer(instance.questions.all(), many=True).data
        response['student'] = StudentSerializer(instance.student).data
        return response


class ResultSerializer(serializers.ModelSerializer):
    exam_name = serializers.CharField(source='exam.name')
    current_year = serializers.CharField(source='exam.current_year')
    exam_session = serializers.CharField(source='exam.examSession')
    current_term = serializers.CharField(source='exam.get_current_term')

    class Meta:
        model = Result
        fields = ['id', 'exam_name', 'marks', 'feedback', 'current_year', 'exam_session', 'current_term', 'exam', 'student', 'department']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['exam'] = ExamSerializer(instance.exam).data
        response['student'] = StudentSerializer(instance.student).data
        response['department'] = DepartmentSerializer(instance.department).data
        return response

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = '__all__'
         
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseWork
        fields = '__all__'

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['department'] = DepartmentSerializer(instance.department).data
        response['file'] = FileSerializer(instance.file).data
        return response

class sessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = session
        fields = ['id', 'name', 'year', 'get_current_term']

class FaqsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faqs
        fields = "__all__"

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpcomingEvents
        fields = "__all__"