from django.contrib.auth.views import LogoutView
from django.urls import path, register_converter
from . import views
from . import converters
from .views import choice_view

register_converter(converters.FourDigitYearConverter, "year4")

urlpatterns = [
    path('', views.index, name='index'),  # главная открытая страница (index.html)
    path('home/', views.home, name='home'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('progress/', views.progress_view, name='progress'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('update-avatar/', views.update_avatar, name='update_avatar'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('create/', views.create, name='create'),
    path('registration/', views.registration, name='registration'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('lesson/<int:chapter_id>/', views.lesson_detail, name='lesson_detail'),
    path('lesson/<int:chapter_id>/done/', views.mark_lesson_done, name='mark_lesson_done'),
    path('choice/<int:choice_id>/', views.choice_view, name='choice'),
    path('choice/<int:choice_id>/done/', views.mark_choice_done, name='mark_choice_done'),
    path('text/<int:text_id>/', views.text_lesson_view, name='text_lesson'),
    path('text/<int:text_id>/done/', views.mark_text_done, name='mark_text_done'),
]