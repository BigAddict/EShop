from django.http import HttpRequest
from management.models import Notification, NotificationItem

def get_notification(request:HttpRequest) -> Notification:
    if request.user.is_authenticated:
        notification, created = Notification.objects.get_or_create(user=request.user)
        if created:
            notification.save()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        notification, created = Notification.objects.get_or_create(session_key=session_key)
        if created:
            notification.save()
    return notification

def add_notification_item(request:HttpRequest, tag:str, message:str, title:str="System"):
    notification = get_notification(request)
    item = NotificationItem.objects.create(notification=notification,
                                           title=title,
                                           tag=tag,
                                           message=message)
    item.save()