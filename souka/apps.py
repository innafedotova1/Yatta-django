from django.apps import AppConfig


class SoukaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'souka'

    def ready(self):
        import souka.signals

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals
