from typing import Any
from django.views.generic import TemplateView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import Product, Topping, Cart, CartItem, Order, OrderItem
from EShop.utils import add_notification_item

class IndexTemplateView(TemplateView):
    template_name = "core/index.html"
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context

class ProductTemplateView(TemplateView):
    template_name = "core/product.html"
    
    def get(self, request: HttpRequest, product_id, *args: Any, **kwargs: Any) -> HttpResponse:
        self.user = request.user
        self.product = get_object_or_404(Product, pk=product_id)
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, product_id:int, *args, **kwargs) -> HttpResponse:
        # Creating or retriving model objects
        self.product = get_object_or_404(Product, pk=product_id)
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
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=self.product)
        
        # Retriving data from post request
        quantity = int(request.POST['quantity'])
        topping_ids = request.POST.getlist('toppings')
        
        if not item_created:
            cart_item.quantity += quantity
        elif item_created:
            cart_item.quantity = quantity
        
        if topping_ids:
            for topping_id in topping_ids:
                topping = get_object_or_404(Topping, pk=topping_id)
                cart_item.toppings.add(topping)
        cart_item.save()
        messages.success(request, f"{self.product.name} added to cart.")
            
        return redirect("index")
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        context['toppings'] = Topping.objects.all()
        return context
    
class CartTemplateView(TemplateView):
    template_name = "core/cart.html"
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            self.cart, created = Cart.objects.get_or_create(user=request.user)
            if created:
                self.cart.save()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            self.cart, created = Cart.objects.get_or_create(session_key=session_key)
            if created:
                self.cart.save()
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            self.cart, created = Cart.objects.get_or_create(user=request.user)
            if created:
                self.cart.save()
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            self.cart, created = Cart.objects.get_or_create(session_key=session_key)
            if created:
                self.cart.save()
        cart_items = self.cart.cartitem_set.all()
        
        # Handle cart update
        for cart_item in cart_items:
            new_quantity = request.POST.get(f"quantity_{cart_item.id}")
            if new_quantity:
                cart_item.quantity = int(new_quantity)
            cart_item.save()
            messages.success(request, "Cart updated!")
        
        # Handle cart item removal
        if request.POST.get('remove_item'):
            item_id_to_remove = request.POST.get('remove_item')
            if item_id_to_remove:
                item_to_remove = get_object_or_404(CartItem, id=item_id_to_remove)
                item_to_remove.delete()
                messages.info(request, f"{item_to_remove.product.name} removed from cart!")
                
        # Handle order placement
        if request.POST.get("order_placed"):
            if request.user.is_authenticated:
                self.order = Order.objects.create(user=request.user)
                self.order.save()
            else:
                session_key = request.session.session_key
                if not session_key:
                    request.session.create()
                    session_key = request.session.session_key
                self.order = Order.objects.create(session_key=session_key)
                if created:
                    self.order.save()
                    
            if request.user.is_authenticated:
                cart = Cart.objects.get(user=request.user)
            else:
                session_key = request.session.session_key
                cart = Cart.objects.get(session_key=session_key)
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                order_item, item_created = OrderItem.objects.get_or_create(order=self.order,
                                                                        product=cart_item.product,
                                                                        quantity=cart_item.quantity)
                for topping in cart_item.toppings.all():
                    order_item.toppings.add(topping)
                order_item.save()
                cart_item.delete()
                messages.success(request, "You've successfully placed an order. Head to the orders page to view your order.")
                add_notification_item(request, 'success', "You've successfully placed an order. Head to the orders page to view your order.", 'Admin')
            redirect("order")
                
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['cart'] = self.cart
        context['cart_items'] = CartItem.objects.filter(cart=self.cart)
        return context
    
class OrderTemplateView(TemplateView):
    template_name = "core/orders.html"
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:   
        if request.user.is_authenticated:
            self.order = Order.objects.filter(user=request.user).prefetch_related('items__product', 'items__toppings')
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            self.order = Order.objects.filter(session_key=session_key).prefetch_related('items__product', 'items__toppings')
        return super().get(request, *args, **kwargs)
    
    def post(self, request: HttpRequest, order_id:Any = None, *args: Any, **kwargs: Any) -> HttpResponse:
        if request.user.is_authenticated:
            self.order = Order.objects.filter(user=request.user).prefetch_related('items__product', 'items__toppings')
        else:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            self.order = Order.objects.filter(session_key=session_key).prefetch_related('items__product', 'items__toppings')
            
        if request.POST.get("order_details"):
            redirect("order_details", order_id)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["orders"] = self.order
        return context
    
class OrderDetailsTemplateView(TemplateView):
    template_name = "core/order_detail.html"
    
    def get(self, request: HttpRequest, order_id, *args: Any, **kwargs: Any) -> HttpResponse:
        self.user = request.user
        self.order = get_object_or_404(Order, pk=order_id)
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['order'] = self.order
        return context