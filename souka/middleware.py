from datetime import date
from .models import UserVisit

class DailyVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            today = date.today()
            UserVisit.objects.get_or_create(user=request.user, date=today)
        return self.get_response(request)
