from django.apps import AppConfig


class MealsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'meals'


from django.apps import AppConfig

class MealsConfig(AppConfig):
    name = 'meals'

    def ready(self):
        import meals.signals
