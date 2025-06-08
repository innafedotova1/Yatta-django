from django.contrib import admin
from .models import Module, Chapter, Lesson, Choice, Text, ChapterProgress, UserVisit, ChoiceImage


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0
    show_change_link = True
    fields = ['title']

@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module')
    inlines = [ChoiceInline]  # ← вот это добавляем

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter')

class ChoiceImageInline(admin.TabularInline):
    model = ChoiceImage
    extra = 0
    max_num = 4

@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter')
    inlines = [ChoiceImageInline]

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'chapter')

#@admin.register(Test)
#class TestAdmin(admin.ModelAdmin):
#    list_display = ('id', 'title', 'chapter')

@admin.register(ChapterProgress)
class ChapterProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'lesson_done', 'choice_1_done', 'choice_2_done', 'text_done')

@admin.register(UserVisit)
class UserVisitAdmin(admin.ModelAdmin):
    list_display = ('user', 'date')
    list_filter = ('date', 'user')
    ordering = ('-date',)

from .models import TaskResult

@admin.register(TaskResult)
class TaskResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'chapter', 'task_type', 'score', 'is_correct', 'submitted_at')
    list_filter = ('task_type', 'submitted_at')



