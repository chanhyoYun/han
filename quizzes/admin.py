from django.contrib import admin
from quizzes.models import *


@admin.action(description="is_pass = True")
def is_pass_true(modeladmin, request, queryset):
    """Django Admin에서 is_pass을 일괄적으로 True 처리"""
    queryset.update(is_pass=True)


class UserQuizAdmin(admin.ModelAdmin):
    list_display = ["pk", "user", "title", "is_pass"]
    ordering = ["is_pass"]
    actions = [is_pass_true]


admin.site.register(UserQuiz, UserQuizAdmin)
admin.site.register(UserQuizoption)
admin.site.register(QuizReport)
