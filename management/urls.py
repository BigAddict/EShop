from django.urls import path

from .views import RegisterTemplateView, LoginTemplateView

urlpatterns = [
    path("register/", RegisterTemplateView.as_view(), name="register"),
    path("login/", LoginTemplateView.as_view(), name="signin")
]