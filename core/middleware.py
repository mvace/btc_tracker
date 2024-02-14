from django.shortcuts import redirect
from django.urls import reverse


class RedirectIfLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path == reverse("login_user"):
            return redirect("index")
        response = self.get_response(request)
        return response
