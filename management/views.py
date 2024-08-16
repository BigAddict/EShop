from typing import Any
from django.db import utils
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from  django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from ESmokies.utils import get_notification, add_notification_item

class RegisterTemplateView(TemplateView):
    template_name = "management/register.html"
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        try:
            user = User.objects.create_user(request.POST.get('username'),
                                            request.POST.get('email'),
                                            request.POST.get("password"))
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
        except utils.IntegrityError:
            messages.error(request, "User already exists")
            redirect("signin")
        except Exception as e:
            messages.error(request, f"The following error occured: {e}")
        return redirect("signin")
    
class LoginTemplateView(TemplateView):
    template_name = "management/login.html"
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        user = authenticate(request,
                            username=request.POST.get("username"),
                            password=request.POST.get("password"))
        if user is not None:
            login(request, user)
            messages.success(request, "You are successfully logged in.")
            add_notification_item(request, "info", f"There was a new login to your account at {user.last_login}")
            next_url = request.GET.get('next')
            if next_url:
                # Redirect to the specified 'next' URL
                return redirect(next_url)
            else:
                # If 'next' is not available, redirect to a default URL
                return redirect('index')
        else:
            messages.error(request, "Incorrect username or password")
            return super().get(request, *args, **kwargs)
        
def signout(request:HttpRequest):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("signin")

class NotificationTemplateView(TemplateView):
    template_name = "management/notifications.html"
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['notification'] = get_notification(self.request)
        return context