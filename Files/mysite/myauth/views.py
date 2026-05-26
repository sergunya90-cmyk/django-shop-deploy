from django.contrib.auth.decorators import (
    login_required,
    permission_required,
    user_passes_test,
)
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LogoutView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    TemplateView,
    CreateView,
    UpdateView,
    ListView,
    DetailView,
)
from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin

from .models import Profile


class AboutMeView(TemplateView):
    template_name = "myauth/about-me.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            Profile.objects.get_or_create(user=self.request.user)
        context["user"] = self.request.user
        return context


class RegisterView(CreateView):
    form_class = UserCreationForm
    template_name = "myauth/register.html"
    success_url = reverse_lazy("myauth:about-me")

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(
            self.request,
            username=username,
            password=password,
        )
        login(request=self.request, user=user)
        return response


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("myauth:login")


class UsersListView(ListView):
    model = User
    template_name = "myauth/user_list.html"
    context_object_name = "users"


class UserDetailView(DetailView):
    model = User
    template_name = "myauth/user_detail.html"
    context_object_name = "user_detail"


class ProfileUpdateView(UserPassesTestMixin, UpdateView):
    model = Profile
    fields = ["avatar", "bio"]
    template_name = "myauth/profile_update.html"

    def test_func(self):
        profile = self.get_object()
        user = self.request.user
        if not user.is_authenticated:
            return False
        return user.is_staff or user.pk == profile.user.pk

    def get_success_url(self):
        return reverse("myauth:user_detail", kwargs={"pk": self.object.user.pk})


@user_passes_test(lambda u: u.is_superuser)
def set_cookie_view(request: HttpRequest) -> HttpResponse:
    response = HttpResponse("Cookie set")
    response.set_cookie("fizz", "buzz", max_age=3600)
    return response


def get_cookie_view(request: HttpRequest) -> HttpResponse:
    value = request.COOKIES.get("fizz", "default value")
    return HttpResponse(f"Cookie value: {value!r}")


@permission_required("myauth.view_profile", raise_exception=True)
def set_session_view(request: HttpRequest) -> HttpResponse:
    request.session["foobar"] = "spameggs"
    return HttpResponse("Session set!")


@login_required
def get_session_view(request: HttpRequest) -> HttpResponse:
    value = request.session.get("foobar", "default")
    return HttpResponse(f"Session value: {value!r}")


class FooBarView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        return JsonResponse({"foo": "bar", "spam": "eggs"})
