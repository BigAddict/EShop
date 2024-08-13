from typing import Any
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect

class RegisterTemplateView(TemplateView):
    template_name = "management/register.html"
    
class LoginTemplateView(TemplateView):
    template_name = "management/login.html"