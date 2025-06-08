from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseNotFound, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db import models
from django.db.models import Q
from datetime import date, timedelta
import json
from .models import (
    Module, Chapter, Lesson, Text, Choice,
    ChapterProgress, UserVisit, UserProfile
)


def has_two_consecutive_days(dates):
    dates = sorted(dates)
    for i in range(1, len(dates)):
        if dates[i] - dates[i - 1] == timedelta(days=1):
            return True
    return False


# контроллеры(функции):
def index(request):
    return render(request, 'souka/index.html')


@login_required
def home(request):
    modules = Module.objects.all()
    progress_qs = ChapterProgress.objects.filter(user=request.user)

    progress_dict = {
        cp.chapter.id: {
            'lesson_done': cp.lesson_done,
            'choice_1_done': cp.choice_1_done,
            'choice_2_done': cp.choice_2_done,
            'text_done': cp.text_done,
        }
        for cp in progress_qs
    }

    return render(request, 'souka/home.html', {
        'modules': modules,
        'progress_dict': progress_dict
    })

def create(request):
    return render(request, 'souka/create.html')


def registration(request):
    return render(request, 'souka/registration.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Имя пользователя уже занято.')
                return redirect('registration')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'Этот email уже используется.')
                return redirect('registration')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                login(request, user)
                return redirect('home')  # Перенаправить на домашнюю страницу после успешной регистрации
        else:
            messages.error(request, 'Пароли не совпадают.')
            return redirect('registration')
    else:
        return redirect('registration')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')  # Перенаправить на главную страницу после входа
            else:
                messages.error(request, 'Неверный пароль.')
                return redirect('login')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')
            return redirect('login')
    else:
        return render(request, 'souka/login.html')


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1>Страница не найдена</h1>")


def lesson_detail(request, chapter_id):
    try:
        lesson = Lesson.objects.select_related('chapter').get(chapter_id=chapter_id)
    except Lesson.DoesNotExist:
        raise Http404("Урок не найден")

    context = {
        'lesson': lesson
    }
    return render(request, 'souka/lesson_detail.html', context)


@require_POST
@login_required
def mark_lesson_done(request, chapter_id):
    chapter = Chapter.objects.get(pk=chapter_id)
    progress, created = ChapterProgress.objects.get_or_create(
        user=request.user,
        chapter=chapter,
        defaults={
            'lesson_done': True,
        }
    )

    if not created:
        progress.lesson_done = True
        progress.save()

    return redirect('home')


@login_required
def achievements_view(request):
    user = request.user
    progress_qs = ChapterProgress.objects.filter(user=user).select_related('chapter')

    words_learned = progress_qs.aggregate(total=models.Sum('words_learned'))['total'] or 0

    visits = list(UserVisit.objects.filter(user=user).values_list('date', flat=True))
    has_streak = has_two_consecutive_days(visits)

    # Список достижений
    achievements = [
        {
            "title": "Путь начинается",
            "description": "Завершите первый урок!",
            "image_true": "progress_1T.png",
            "image_false": "progress_1F.png",
            "completed": progress_qs.filter(chapter__id=1, lesson_done=True).exists()
        },
        {
            "title": "6 слов мудрости",
            "description": "Выучить 6 слов",
            "image_true": "progress_2T.png",
            "image_false": "progress_2F.png",
            "completed": words_learned >= 6
        },
        {
            "title": "Огонь привычки",
            "description": "Учиться 2 дня подряд",
            "image_true": "progress_3T.png",
            "image_false": "progress_3F.png",
            "completed": has_streak,
        },
    ]

    # Подсчёт выполненных
    completed_count = sum(1 for a in achievements if a["completed"])

    return render(request, 'souka/achievements.html', {
        'achievements': achievements,
        'completed_count': completed_count
    })


def progress_view(request):
    return render(request, 'souka/progress.html')


@login_required
def progress_view(request):
    active_days = UserVisit.objects.filter(user=request.user).count()

    chapter_progress = ChapterProgress.objects.filter(user=request.user)

    completed_lessons = sum([
        cp.lesson_done +
        cp.choice_1_done +
        cp.choice_2_done +
        cp.text_done
        for cp in chapter_progress
    ])

    lessons_without_errors = sum([
        cp.choice_1_perfect +
        cp.choice_2_perfect +
        cp.text_perfect
        for cp in chapter_progress
    ])

    words_learned = chapter_progress.aggregate(
        total=models.Sum('words_learned')
    )['total'] or 0

    visited_today = UserVisit.objects.filter(
        user=request.user,
        date=date.today()
    ).exists()

    if visited_today:
        words_today = ChapterProgress.objects.filter(
            user=request.user,
            words_learned__gt=0
        ).aggregate(
            total=models.Sum('words_learned')
        )['total'] or 0
    else:
        words_today = 0

    return render(request, 'souka/progress.html', {
        'active_days': active_days,
        'completed_lessons': completed_lessons,
        'lessons_without_errors': lessons_without_errors,
        'words_learned': words_learned,
        'words_today': words_today,
    })


@login_required
def profile_view(request):
    user = request.user

    active_days = UserVisit.objects.filter(user=user).count()
    completed_lessons = ChapterProgress.objects.filter(user=user, lesson_done=True).count()
    chapter_progress = ChapterProgress.objects.filter(user=user)

    lessons_without_errors = sum([
        cp.choice_1_perfect +
        cp.choice_2_perfect +
        cp.text_perfect
        for cp in chapter_progress
    ])

    words_learned = ChapterProgress.objects.filter(user=user).aggregate(
        total=models.Sum('words_learned')
    )['total'] or 0

    visits = list(UserVisit.objects.filter(user=user).values_list('date', flat=True))
    has_streak = has_two_consecutive_days(visits)

    achievements = [
        {
            "title": "Путь начинается",
            "description": "Завершите первый урок!",
            "image_true": "progress_1T.png",
            "image_false": "progress_1F.png",
            "completed": ChapterProgress.objects.filter(user=user, chapter__id=1, lesson_done=True).exists()
        },
        {
            "title": "6 слов мудрости",
            "description": "Выучить 6 слов",
            "image_true": "progress_2T.png",
            "image_false": "progress_2F.png",
            "completed": words_learned >= 6
        },
        {
            "title": "Огонь привычки",
            "description": "Учиться 2 дня подряд",
            "image_true": "progress_3T.png",
            "image_false": "progress_3F.png",
            "completed": has_streak,
        },
    ]

    return render(request, 'souka/profile.html', {
        'active_days': active_days,
        'completed_lessons': completed_lessons,
        'lessons_without_errors': lessons_without_errors,
        'achievements': achievements,
        'words_learned': words_learned,
    })


@login_required
def settings_view(request):
    user = request.user
    avatar_choices = ['ava_1.png', 'ava_2.png', 'ava_3.png']
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        if request.POST.get('avatar') in avatar_choices:
            user.profile.avatar = request.POST['avatar']
            user.profile.save()

        if 'first_name' in request.POST:
            username = request.POST.get('first_name').strip()
            email = request.POST.get('email').strip()

            if username != user.username and User.objects.filter(username=username).exclude(pk=user.pk).exists():
                messages.error(request, "Имя пользователя уже занято.")
            elif email != user.email and User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, "Email уже используется.")
            else:
                user.username = username
                user.email = email
                user.save()
                messages.success(request, "Данные профиля успешно обновлены.")

        if 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Пароль успешно изменён.")
            else:
                messages.error(request, "Ошибка при смене пароля. Проверьте введённые данные.")

        return redirect('settings')

    return render(request, 'souka/settings.html', {
        'user': user,
        'avatar_choices': avatar_choices,
        'password_form': password_form,
    })


@csrf_exempt
@login_required
def update_avatar(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_avatar = data.get("avatar")
        avatar_choices = ['ava_1.png', 'ava_2.png', 'ava_3.png']
        if new_avatar in avatar_choices:
            request.user.profile.avatar = new_avatar
            request.user.profile.save()
            return JsonResponse({"status": "ok"})
        return JsonResponse({"error": "invalid avatar"}, status=400)


def choice_view(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    return render(request, 'souka/choice.html', {'choice': choice})


@require_POST
@login_required
def mark_choice_done(request, choice_id):
    choice = get_object_or_404(Choice, id=choice_id)
    chapter = choice.chapter

    progress, created = ChapterProgress.objects.get_or_create(
        user=request.user,
        chapter=chapter
    )

    choices = list(chapter.choices.order_by('id'))
    first_choice = choices[0] if len(choices) > 0 else None
    second_choice = choices[1] if len(choices) > 1 else None

    perfect = request.POST.get("perfect") == "true"
    words_added = 0

    if first_choice and choice.id == first_choice.id:
        if not progress.choice_1_done:
            words_added = 1
        progress.choice_1_done = True
        if perfect:
            progress.choice_1_perfect = True

    elif second_choice and choice.id == second_choice.id:
        if not progress.choice_2_done:
            words_added = 1
        progress.choice_2_done = True
        if perfect:
            progress.choice_2_perfect = True

    progress.words_learned += words_added
    progress.save()
    return redirect('home')


@require_POST
@login_required
def mark_text_done(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    chapter = text.chapter

    progress, created = ChapterProgress.objects.get_or_create(
        user=request.user,
        chapter=chapter
    )

    perfect = request.POST.get("perfect") == "true"
    words_added = 0

    # Засчитываем слово, если это первое прохождение
    if not progress.text_done:
        words_added = 1

    progress.text_done = True

    if perfect:
        progress.text_perfect = True

    progress.words_learned += words_added
    progress.save()
    return redirect('home')


def text_lesson_view(request, text_id):
    text = get_object_or_404(Text, id=text_id)
    return render(request, 'souka/text.html', {'text': text})
