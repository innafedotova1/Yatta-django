from django.db import models
from django.contrib.auth.models import User


class Module(models.Model):
    title = models.CharField("Название модуля", max_length=255)

    def __str__(self):
        return self.title


class Chapter(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField("Название главы", max_length=255)

    def __str__(self):
        return f"{self.module.title} — {self.title}"


class Lesson(models.Model):
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name='lesson')
    title = models.CharField("Название урока", max_length=255)
    video = models.FileField("Видео", upload_to='videos/')
    description = models.TextField("Описание к уроку")

    def __str__(self):
        return self.title


class Choice(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='choices')
    title = models.CharField("Интерактив: выбор", max_length=255)

    def __str__(self):
        return self.title

class ChoiceImage(models.Model):
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='choice_images/')
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Картинка для '{self.choice.title}' ({'верно' if self.is_correct else 'неверно'})"


class Text(models.Model):
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name='text')
    title = models.CharField("Текстовое задание", max_length=255)
    content = models.TextField("Иероглиф")  # Это будет отображаться как задание
    correct_answers = models.TextField("Правильные ответы (через запятую)", blank=True, null=True)
    audio = models.FileField(upload_to='audio/', blank=True, null=True)

    def __str__(self):
        return self.title

    def get_correct_answers(self):
        if not self.correct_answers:
            return []
        return [ans.strip().lower() for ans in self.correct_answers.split(',')]

    def get_first_answer(self):
        if not self.correct_answers:
            return ""
        return self.correct_answers.split(',')[0].strip()


class Test(models.Model):
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name='test')
    title = models.CharField("Тест", max_length=255)

    def __str__(self):
        return self.title


class TaskResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=10, choices=[('choice', 'Choice'), ('text', 'Text'), ('test', 'Test')])
    is_correct = models.BooleanField(default=False)
    score = models.PositiveIntegerField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chapter', 'task_type')

    def __str__(self):
        return f"{self.user.username} - {self.chapter} - {self.task_type}"


class ChapterProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    lesson_done = models.BooleanField(default=False)
    choice_1_done = models.BooleanField(default=False)
    choice_2_done = models.BooleanField(default=False)
    choice_1_perfect = models.BooleanField(default=False)
    choice_2_perfect = models.BooleanField(default=False)
    text_done = models.BooleanField(default=False)
    words_learned = models.PositiveIntegerField(default=0)
    test_done = models.BooleanField(default=False)
    text_perfect = models.BooleanField(default=False)
    score = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'chapter')

    def __str__(self):
        return f"{self.user.username} - {self.chapter.title}"


class UserVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')  # один визит в день

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.CharField(max_length=100, default='ava_1.png')