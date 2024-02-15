from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RedirectIfLoggedInMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.path == reverse("login_user"):
            messages.success(request, ("You're already logged in or registered"))
            return redirect("index")
        response = self.get_response(request)
        return response
