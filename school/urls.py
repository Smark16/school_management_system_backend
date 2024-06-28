from django.urls import path
from . import views  # Make sure this import is correct

urlpatterns = [
 #user urls
    path('', views.ObtainPairView.as_view()),
    path('student_register', views.StudentRegisterView.as_view()),
    path('teacher_register', views.TeacherRegisterView.as_view()),
    path('delete_user/<int:pk>/', views.DeleteAccount.as_view()),
    path("update_user/<int:pk>", views.updateUser.as_view()),
    path("get_user/<int:pk>", views.getUser.as_view()),
    path("all_users", views.AllUsers.as_view()),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),

    #student view
    path('students', views.StudentView.as_view()),
    path('student_total/<int:pk>', views.studentTotal.as_view()),
    path('update_student/<int:pk>', views.UpdateStudent.as_view()),
    path("retrieve_student/<int:pk>", views.retriveStudent.as_view()),
    path("removed_students", views.removedStudents),

    #teacher view
    path('teachers', views.TeacherView.as_view()),
    path('update_teacher/<int:pk>', views.UpdateTeacher.as_view()),
    path("retrieve_teacher/<int:pk>", views.retrieveTeacher.as_view()),
    path('teacher_by_department/<int:dept_id>', views.get_teacher_department),

    #department view
    path('departments', views.DepartmentView.as_view()),
    path('single_dept/<int:pk>', views.retrieveDepartment.as_view()),
    path('post_department', views.postDepartments.as_view()),

    #exam view
    path('exams', views.ExamView.as_view()),
    # path('post_exams', views.postExam.as_view()),
    path('exam_department_count/<int:dept_id>', views.exam_department_count),
    path('dept_exams/<int:dept_id>', views.get_deptExams),
    path('exam_questions/<int:pk>', views.ExamQuestions.as_view()),
    # path('single_exam_department/<int:id>', views.SingleExam),
    path('update_status/<int:pk>', views.UpdateStatus.as_view()),
    path('updateExam/<int:pk>', views.UpdateExam.as_view()),
    path("post_exam", views.post_exam),

    #results
    path('results', views.ResultView.as_view()),
    path('new_results', views.postResults.as_view()),
    path('department_results/<int:department>', views.RetrieveDepartmentResult),
    path('retrieve_department_results/<int:department_id>', views.retrieve_department_results),
    path('student_results/<int:stud_id>', views.student_results),
    path('get_student_user/<int:userId>', views.get_student_user),
    path('get_report/<int:stud_id>', views.get_report),
    path('department_perfomance/<int:department_id>', views.departmentPerfomancePercentage),
    path('student_performance/<int:student_id>', views.student_performance),
  
    #questions
    path('questions', views.QuestionView.as_view()),
    path('post_questions', views.postQuestion.as_view()),
    path('edit_question/<int:pk>', views.updateQuestion.as_view()),
    path('delete_question/<int:pk>',views.deleteQuestion.as_view()),
    # path('questions/<int:teacher_id>/<int:department_id>', views.get_filtered_questions),
    path('update_answer/<int:pk>', views.UpdateAnswer.as_view()),
    path('update_question/<int:pk>', views.UpdateQuestion.as_view()),
    path("get_teacher_questions/<int:teacher_id>/<int:department_id>", views.get_teacher_questions),

    #coursework
    path('courseworks', views.CourseWorks.as_view()),
    path('post_work', views.postWork.as_view()),
    path('download_file/<int:file_id>', views.download_file, name='download_file'),
    path('department_files/<int:dept_id>', views.get_department_files, name='get_department_files'),

    # exam sessions
    path('exam_session', views.ExamSessions.as_view()),

    # faqs
    path('faqs', views.FaqsView.as_view()),

    # upcoming events
    path("upcoming_events", views.Event_View.as_view()),
    path("post_events", views.PostEvents.as_view()),
    path("delete_event/<int:pk>", views.deleteEvent.as_view()),
    path("edit_event/<int:pk>", views.editEvent.as_view()),

    #file urls
    path("all_files", views.AllFiles.as_view()),
    path("upload_file", views.UploadFile.as_view()),

]