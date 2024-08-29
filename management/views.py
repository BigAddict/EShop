from typing import Any
from phonenumber_field.modelfields import PhoneNumberField
from django.db import utils
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from  django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from EShop.utils import add_notification_item
from .models import NotificationItem, UserMessage

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
        print(request.content_params)
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.POST.get('remove_notification'):
            notification_id_to_remove = request.POST.get('remove_notification')
            if notification_id_to_remove:
                notification_to_remove = get_object_or_404(NotificationItem, id=notification_id_to_remove)
                notification_to_remove.delete()
        return super().get(request, *args, **kwargs)
    
class ContactTemplateView(TemplateView):
    template_name = "management/contacts.html"
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        phone_number = request.POST.get('phone_number')
        sent_message = request.POST.get('message')
        message = UserMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            phone_number=phone_number,
            message=sent_message
        )
        try:
            message.save()
            messages.success(request, "Your message was successfully sent")
            add_notification_item(request, "success", "Your message was successfully sent.", "Admin")
        except Exception as e:
            messages.error(request, e)
            add_notification_item(request, "success", f"The following error occured while sending your message.\n {e}.\n Please contact the admin.")
        return super().get(request, *args, **kwargs)