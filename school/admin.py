from django.contrib import admin
from .forms import StudentCreationForm, TeacherCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *

# Register your models here.
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'is_student', 'is_teacher', 'is_headteacher')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_student', 'is_teacher', 'is_headteacher')}),
    )
    add_fieldsets = (
        (None, {'fields': ('username', 'email', 'password1', 'password2')}),
        ('Permissions', {'fields': ('is_student', 'is_teacher', 'is_headteacher')}),
    )

class StudentAdmin(admin.ModelAdmin):
    form = StudentCreationForm
    list_display = ('id','name', 'reg_no', 'student_no', 'dob', 'year_of_enrollment', 'user')
    list_filter = ('year_of_enrollment',)
    search_fields = ('name', 'reg_no', 'student_no')

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'code', 'term', 'description']

class TeacherAdmin(admin.ModelAdmin):
    form = TeacherCreationForm
    list_display = ('id','user', 'department', 'email')
    list_filter = ('department',)
    search_fields = ('user__username', 'email')

class ExamAdmin(admin.ModelAdmin):
    filter_horizontal = ("questions", )
    list_display = ['id', 'name', 'department', 'duration', 'get_questions','date', 'status', 'submission_Time', 'get_current_term']

    def get_questions(self, obj):
        return ", ".join([questions.text for questions in obj.questions.all()])
    get_questions.short_description = 'questions'  # Optional: to provide a header for the column


class ResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'exam', 'marks', 'feedback']

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'option_1', 'option_2', 'option_3', 'option_4', 'option_5', 'ans']

class FileUploadAdmin(admin.ModelAdmin):
    list_display = ["name", "department", "description", "file", "uploaded_at"]

class sessionAdmin(admin.ModelAdmin):
    list_display =  ['id', 'name', 'year', 'get_current_term']

class FaqsAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'answer']

class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'startDate', 'endDate', 'files', 'image', 'location']

class FileAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

admin.site.register(User, UserAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Teacher, TeacherAdmin)
admin.site.register(Exam, ExamAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Question,QuestionAdmin)
admin.site.register(CourseWork, FileUploadAdmin)
admin.site.register(session, sessionAdmin)
admin.site.register(Faqs, FaqsAdmin)
admin.site.register(UpcomingEvents, EventAdmin)
admin.site.register(FileUpload, FileAdmin)