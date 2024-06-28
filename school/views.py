from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse, FileResponse
from rest_framework.response import Response
from rest_framework import generics
from .models import *
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission
from django.http import FileResponse, Http404
from collections import defaultdict
from .models import User
from rest_framework.authentication import TokenAuthentication
import logging
import os
from django.conf import settings
from django.utils.dateparse import parse_duration
from django.db.models import Avg


logger = logging.getLogger(__name__)

# Create your views here.
class ObtainPairView(TokenObtainPairView):
    serializer_class = ObtainSerializer

class AllUsers(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# user actions
class DeleteAccount(generics.DestroyAPIView):
    queryset = User.objects.all()

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Update 'removed' field for Student or Teacher based on instance type
        if hasattr(instance, 'student'):
            instance.student.removed = True
            instance.student.save()
        elif hasattr(instance, 'teacher'):
            instance.teacher.removed = True
            instance.teacher.save()

        # Actually delete the User instance
        self.perform_destroy(instance)

        return Response({"detail": "User account deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()

class getUser(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class updateUser(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs["pk"])
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def put(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.update(user, serializer.validated_data)
            return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentRegisterView(generics.CreateAPIView):
    queryset = Student.objects.all()
    permission_classes = [AllowAny]
    serializer_class = StudentRegistration

    
class TeacherRegisterView(generics.CreateAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TeacherRegistration


#student view
class StudentView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

@api_view(['GET'])
def removedStudents(request):
    total_students = Student.objects.count()
    removed_students = Student.objects.filter(removed=True).count()
    percentage_removed = (removed_students / total_students) * 100 if total_students > 0 else 0
    return Response({
        "total_students": total_students,
        "removed_students": removed_students,
        "percentage_removed": percentage_removed
    }, status=status.HTTP_200_OK)

# get total students based on there department
class studentTotal(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['GET'])
def get_student_user(request, userId):
    try:
        loggedStudent = Student.objects.get(user = userId)
    except Student.DoesNotExist:
        return Response({"err:student not found"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = StudentSerializer(loggedStudent)
        return Response(serializer.data)
    
class UpdateStudent(generics.UpdateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class retriveStudent(generics.RetrieveAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer  = self.get_serializer(instance)
        return Response(serializer.data)

#teacher view
class TeacherView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class UpdateTeacher(generics.UpdateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
    
class retrieveTeacher(generics.RetrieveAPIView):
    queryset = Teacher.objects.all()
    permission_classes = [AllowAny]
    serializer_class = TeacherSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
        except Teacher.DoesNotExist:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_teacher_department(request, dept_id):
    try:
        teacher = Teacher.objects.filter(department=dept_id)
    except Teacher.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = TeacherSerializer(teacher, many=True)
        return Response(serializer.data)


#department view
class DepartmentView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class retrieveDepartment(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class postDepartments(APIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

    def post(self, request, format=None):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

#exam view
class ExamView(generics.ListAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    
    # new post view
@api_view(['POST'])
def post_exam(request):
    questions = request.data.get('questions', [])
    logger.debug(f"Received questions: {questions}")

    exam = Exam.objects.create(
        name=request.data['name'],
        duration=parse_duration(request.data['duration']),
        date=request.data['date'],
        description=request.data['description'],
        week=request.data['week'],
        examSession=request.data['examSession'],
        department_id=request.data['department'],
    )

    for question_id in questions:
        try:
            question = Question.objects.get(id=question_id)
            question.used_in_exam = True
            question.save()
            exam.questions.add(question)
        except Question.DoesNotExist:
            logger.error(f"Question with ID {question_id} does not exist")

    exam.save()

    return Response(
        {"message": "Exam created successfully!", "exam_id": exam.id},
        status=status.HTTP_201_CREATED,
    )

    
class UpdateExam(generics.UpdateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
    
@api_view(['GET'])
def exam_department_count(self, dept_id):
    try:
        exams_count = Exam.objects.filter(department=dept_id).count()
        return Response({"count":exams_count}, status=status.HTTP_200_OK)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_deptExams(request, dept_id):
    try:
        exams = Exam.objects.filter(department=dept_id)
    except Exam.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializer = ExamSerializer(exams, many=True)
        return Response(serializer.data)
    
class ExamQuestions(generics.RetrieveAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
# @api_view(['GET'])
# def SingleExam(request, id):
#     try:
#         exam = Exam.objects.get(department=id)
#     except Exam.DoesNotExist:
#         return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)

#     if request.method == 'GET':
#         serializer = ExamSerializer(exam)
#         return Response(serializer.data)

class UpdateQuestion(APIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def patch(self, request, *args, **kwargs):
        exam_id = kwargs.get('pk')

        try:
            exam = Exam.objects.get(pk=exam_id)
            questions_data = request.data.get('questions')  # Get the list of question IDs from the request body

            if not isinstance(questions_data, list):
                return Response({"error": "Questions should be a list of question IDs."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the questions from the database
            questions = Question.objects.filter(id__in=questions_data)

            # Update the exam's questions
            exam.questions.set(questions)
            exam.save()

            serializer = self.serializer_class(exam)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exam.DoesNotExist:
            return Response({"error": "Exam not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
# update status
class UpdateStatus(APIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer

    def patch(self, request, *args, **kwargs):
        get_exam_id = kwargs.get('pk')     
        status = request.data.get('status')

        try:
            examStatus = Exam.objects.get(pk = get_exam_id)    
            examStatus.status = status
            examStatus.save()

            serializer = self.serializer_class(examStatus)
            return Response(serializer.data)   
        except Exam.DoesNotExist:
            return Response({"err:Not found"})
        
#result view
class ResultView(generics.ListAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class postResults(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format=None):
        serializers = ResultSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
          
@api_view(['GET'])
def RetrieveDepartmentResult(request, department):
    try:
        departmentResults = Result.objects.filter(department=department).order_by('-marks')
    except Result.DoesNotExist:
         return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serialize = ResultSerializer(departmentResults, many=True)
        return Response(serialize.data)
    
@api_view(['GET'])
def retrieve_department_results(request, department_id):
    try:
        department_results = Result.objects.filter(department=department_id)
        serializer = ResultSerializer(department_results, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Result.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

# perfomance rate
@api_view(['GET'])
def student_performance(request, student_id):
    student = Student.objects.get(id=student_id)
    results = Result.objects.filter(student=student)

    # Calculate average score for each subject
    subject_performance = results.values('exam').annotate(average_score=Avg('marks'))

    # Find the subject with the highest average score
    best_subject = max(subject_performance, key=lambda x: x['average_score'])

    # Fetch the subject name for the best subject
    best_subject_name = Exam.objects.get(id=best_subject['exam']).name

    context = {
        'student': {
            'id': student.id,
            'name': student.name,
        },
        'subject_performance': [
            {
                'subject_name': Exam.objects.get(id=subject['exam']).name,
                'average_score': subject['average_score'],
                'department':Exam.objects.get(id=subject['exam']).department.name
            } for subject in subject_performance
        ],
        'best_subject': {
            'subject_name': best_subject_name,
            'average_score': best_subject['average_score']
        }
    }

    return Response(context)
    
@api_view(['GET'])
def calculate_department_average_marks(request, department_id):
    try:
        department_results = Result.objects.filter(department=department_id)
        total_marks = sum(result.marks for result in department_results)
        average_marks = total_marks / len(department_results)
        return Response({'average_marks': average_marks}, status=status.HTTP_200_OK)
    except Result.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def student_results(request, stud_id):
    results = Result.objects.filter(student_id=stud_id).select_related('exam')
    serialized_results = ResultSerializer(results, many=True).data

    # Group results by session
    sessions = defaultdict(lambda: {'results': []})
    for result in serialized_results:
        session_key = f"{result['current_year']}-{result['exam_session']}-{result['current_term']}"
        if 'year' not in sessions[session_key]:
            sessions[session_key].update({
                'year': result['current_year'],
                'name': result['exam_session'],
                'term': result['current_term'],
            })
        sessions[session_key]['results'].append({
            'id': result['id'],
            'exam_name': result['exam_name'],
            'marks': result['marks'],
            'feedback': result['feedback'],
        })

    return JsonResponse(list(sessions.values()), safe=False)

@api_view(['GET'])
def get_report(request, stud_id):
    try:
        result = Result.objects.filter(student = stud_id)
    except Result.DoesNotExist:
        return Response({"err:No student result found"})
    if request.method == 'GET':
        serializers = ResultSerializer(result, many=True)
        return Response(serializers.data)

@api_view(['GET'])
def departmentPerfomancePercentage(request, department_id):
    try:
        # Get all students in the department
        department_students = Student.objects.all()
        total_students_count = department_students.count()
        if total_students_count == 0:
            return Response({'percentage': 0})  # Return 0 if no students found

        # Get all exams for the department
        department_exams = Exam.objects.filter(department=department_id)
        if not department_exams.exists():
            return Response({'percentage': 0})  # Return 0 if no exams found

        total_results_80_count = 0  # Initialize count for results with score >= 80

        for exam in department_exams:
            # Count results with score >= 80 for each exam
            results_80_count = Result.objects.filter(exam=exam, marks__gte=80).count()
            total_results_80_count += results_80_count

        # Calculate the performance percentage based on '80 and above' scores
        performance_percentage = (total_results_80_count / total_students_count) * 100 

        return Response({'percentage': performance_percentage})

    except Exception as e:
        # Handle exceptions or errors appropriately
        print(f"Error in calculating department performance percentage: {e}")
        return Response({'error': 'Failed to calculate performance percentage'}, status=500)
    
#question view
class QuestionView(generics.ListAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

class postQuestion(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        serializers = QuestionSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
class updateQuestion(generics.UpdateAPIView):
    queryset = Question.objects.all()
    serializer_class  = QuestionSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

class deleteQuestion(generics.DestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    #new get view 
@api_view(['GET'])
def get_teacher_questions(request, teacher_id, department_id):
    questions = Question.objects.filter(teacher_id=teacher_id, department_id=department_id, used_in_exam=False)
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)

# update Answer
class UpdateAnswer(APIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def patch(self, request, *args, **kwargs):
        qtn_id = kwargs.get('pk')
        answer = request.data.get("ans")

        try:
            question = Question.objects.get(pk=qtn_id)
            question.ans = answer
            question.save()

            serializer = self.serializer_class(question)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({"error": "Question Not found"}, status=status.HTTP_404_NOT_FOUND)

# coursework view
class CourseWorks(generics.ListAPIView):
    queryset = CourseWork.objects.all()
    serializer_class = CourseSerializer

class postWork(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializers = CourseSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def download_file(request, file_id):
    try:
        coursework = CourseWork.objects.get(file__id=file_id)
        file_upload = coursework.file
        response = FileResponse(file_upload.name.open('rb'), as_attachment=True, filename=file_upload.name.name)
        return response
    except CourseWork.DoesNotExist:
        return Response({'error': 'File not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def get_department_files(request, dept_id):
    try:
        files = CourseWork.objects.filter(department=dept_id)
    except CourseWork.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        serializers = CourseSerializer(files, many=True)
        return Response(serializers.data)
    
# exam sessions
class ExamSessions(generics.ListAPIView):
    queryset = session.objects.all()
    serializer_class = sessionSerializer

# faqs part
class FaqsView(generics.ListAPIView):
    queryset = Faqs.objects.all()
    serializer_class = FaqsSerializer

# event serializer
class Event_View(generics.ListAPIView):
    queryset = UpcomingEvents.objects.all()
    serializer_class = EventSerializer

class PostEvents(APIView):
    queryset = UpcomingEvents.objects.all()
    serializer_class = EventSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class deleteEvent(generics.DestroyAPIView):
    queryset = UpcomingEvents.objects.all()
    serializer_class = EventSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class editEvent(generics.UpdateAPIView):
    queryset = UpcomingEvents.objects.all()
    serializer_class = EventSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.serializer_class(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
#manage files
class AllFiles(generics.ListAPIView):
    queryset = FileUpload.objects.all()
    serializer_class = FileSerializer

class UploadFile(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            file_instance = serializer.save()
            file_url = request.build_absolute_uri(file_instance.name.url)
            return Response({
                "file_id": file_instance.id,
                "file_url": file_url
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    