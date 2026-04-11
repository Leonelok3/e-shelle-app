from django.contrib import admin
from .models import Lesson, Exercise, Exam, Question, PastPaper


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "class_level", "subject", "status")
    list_filter = ("class_level", "subject", "status")
    search_fields = ("title",)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("title", "class_level", "subject", "status")
    inlines = [QuestionInline]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("title", "class_level", "subject", "duration_minutes", "status")
    inlines = [QuestionInline]


@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ("exam_type", "year", "subject", "class_level")
    list_filter = ("exam_type", "year", "subject")
