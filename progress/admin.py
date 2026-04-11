from django.contrib import admin
from .models import Attempt, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "attempt_type", "exercise", "exam", "score", "max_score", "created_at")
    list_filter = ("attempt_type", "created_at")
    search_fields = ("user__username",)
    inlines = [AnswerInline]
    ordering = ("-created_at",)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "correct", "question_preview", "given_preview")
    list_filter = ("correct",)
    search_fields = ("attempt__user__username",)

    @admin.display(description="Question")
    def question_preview(self, obj):
        return (obj.question_text[:60] + "...") if len(obj.question_text) > 60 else obj.question_text

    @admin.display(description="Réponse")
    def given_preview(self, obj):
        return (obj.given_answer[:60] + "...") if len(obj.given_answer) > 60 else obj.given_answer
