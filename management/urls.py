from django.urls import path

from .views import RegisterTemplateView, LoginTemplateView, signout, NotificationTemplateView, ContactTemplateView

urlpatterns = [
    path("", LoginTemplateView.as_view(), name="signin"),
    path("register/", RegisterTemplateView.as_view(), name="register"),
    path("logout/", signout, name="signout"),
    path("notification/", NotificationTemplateView.as_view(), name="notification"),
    path("contacts/", ContactTemplateView.as_view(), name="contacts")
]