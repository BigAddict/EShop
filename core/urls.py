from django.urls import path

from .views import IndexTemplateView, ProductTemplateView, CartTemplateView, OrderTemplateView, OrderDetailsTemplateView

urlpatterns = [
    path("", IndexTemplateView.as_view(), name="index"),
    path("<int:product_id>/", ProductTemplateView.as_view(), name="product"),
    path("cart/", CartTemplateView.as_view(), name="cart"),
    path("order/", OrderTemplateView.as_view(), name="order"),
    path("order/<int:order_id>/", OrderDetailsTemplateView.as_view(), name="order_detail")
]
