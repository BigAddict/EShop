from django.urls import path

from .views import RegisterTemplateView, LoginTemplateView, signout, NotificationTemplateView

urlpatterns = [
    path("register/", RegisterTemplateView.as_view(), name="register"),
    path("login/", LoginTemplateView.as_view(), name="signin"),
    path("logout/", signout, name="signout"),
    path("notification/", NotificationTemplateView.as_view(), name="notification")
]