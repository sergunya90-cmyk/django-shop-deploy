from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse
from django.urls import reverse_lazy

class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")

def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set!")
    response.set_cookie("my_cookie_key", "cookie_value_123", max_age=3600)
    return response

def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("my_cookie_key", "default_cookie_value")
    return HttpResponse(f"Cookie value: {value}")

def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["my_session_key"] = "session_value_456"
    return HttpResponse("Session set!")

def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("my_session_key", "default_session_value")
    return HttpResponse(f"Session value: {value}")