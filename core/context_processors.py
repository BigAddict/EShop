from django.http import HttpRequest

from .models import Cart, CartItem
from EShop.utils import get_notification

def custom_processor(request: HttpRequest) -> dict:
    context = {}
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        if created:
            cart.save()
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        if created:
            cart.save()
            
    context['cart'] = cart
    context['cart_item_count'] = CartItem.objects.filter(cart=cart).count()
    context['cart_items'] = CartItem.objects.filter(cart=cart)
    context['notification'] = get_notification(request)
    return context