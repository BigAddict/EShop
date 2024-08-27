from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _

UserModel = get_user_model()
class Notification(models.Model):

    user = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("User Buying"))
    session_key = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        verbose_name = _("Notification")
        verbose_name_plural = _("Notifications")

    def __str__(self):
        return f"{self.user.username if self.user else self.session_key} Notification"

class NotificationItem(models.Model):

    TAGS = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="items")
    title = models.CharField(_("Notification Title"), max_length=20, default="System")
    tag = models.CharField(_("Notification Tag"), choices=TAGS, default="info", max_length=10)
    message = models.TextField(_("Notification content"))
    created_on = models.DateTimeField(auto_now_add=True)
    
    def shortened_message(self):
        return f"{self.message[:30]}..."

    class Meta:
        verbose_name = _("NotificationItem")
        verbose_name_plural = _("NotificationItems")

    def __str__(self):
        return f"{self.tag.title} notification for {self.notification.user.username if self.notification.user else self.notification.session_key}"

class UserMessage(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    email= models.EmailField(_("Email"), max_length=254)
    subject = models.CharField(_("Subject"), max_length=500)
    phone_number = PhoneNumberField(region="KE")
    message = models.TextField(_("Message"))
    
    def __str__(self) -> str:
        return f"{self.email}'s message."