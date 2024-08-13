from django.db import models
from django.contrib.auth import get_user_model
from PIL import Image
from django.core.exceptions import ValidationError
from io import BytesIO
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from PIL import Image

UserModel = get_user_model()

# class ProductCategory(models.Model):
#     name = models.CharField(_("Category Name"), max_length=100)
    
#     class Meta:
#         verbose_name = "Product Category"
#         verbose_name_plural = "Product Categories"
        
#     def __str__(self) -> str:
#         return f"{self.name} Category"

class Product(models.Model):
    name = models.CharField(_("Product Name"), max_length=100)
    # category = models.ForeignKey(ProductCategory, verbose_name=_("Product Category"), on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(_("Product Description"), blank=True)
    photo = models.ImageField(_("Product Photo"), upload_to="product_photos", blank=True, )
    price = models.PositiveIntegerField(_("Product Price"))
    
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        
    def save(self, *args, **kwargs):
        # Validate and optimize the image
        if self.photo:
            # Open the image file
            img = Image.open(self.photo)
            
            # Check image dimensions
            img = img.resize((270, 270))

            # Optimize the image
            img = img.convert('RGB')  # Ensure the image is in RGB mode
            img_io = BytesIO()  # Create a BytesIO buffer to hold the optimized image
            img.save(img_io, format='JPEG', quality=85, optimize=True)  # Save the image with optimization
            img_content = ContentFile(img_io.getvalue(), name=self.photo.name)  # Create a ContentFile for the optimized image

            # Replace the image with the optimized version
            self.photo.save(name=self.photo.name, content=img_content, save=False)

        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.name} @ {self.price}"
    
class Topping(models.Model):
    name = models.CharField(_("Topping Name"), max_length=50)
    photo = models.ImageField(_("Topping Photo"), upload_to="topping_photos", blank=True)
    price = models.DecimalField(_("Price"), max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name
        
class Cart(models.Model):
    user = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("User Buying"))
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ManyToManyField(Product, through='CartItem')
    
    def grand_total(self):
        return round(sum(item.product.price * item.quantity for item in self.cartitem_set.all()), 2)
    
    def __str__(self):
        return f"{self.user.username if self.user else self.session_key}'s Cart"
        
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    toppings = models.ManyToManyField(Topping, through='ProductTopping')
    quantity = models.PositiveIntegerField(default=1)
    
    def total_price(self):
        return round(self.product.price * self.quantity, 2)
    
    def __str__(self) -> str:
        return f"{self.quantity} X {self.product.name}"
    
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packaged', 'Packaged'),
        ('picked_up', 'Picked Up'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(UserModel, null=True, blank=True, on_delete=models.CASCADE, verbose_name=_("User Buying"))
    session_key = models.CharField(max_length=40, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    def grand_total(self):
        return round(sum(item.product.price * item.quantity for item in self.items.all()), 2)
    
    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
    
    def __str__(self) -> str:
        return f"{self.user.username if self.user else self.session_key}'s Order on {self.order_date}"
    
    def update_status(self):
        statuses = self.items.values_list('status', flat=True)
        if all(status == 'packaged' for status in statuses):
            self.status = 'packaged'
        elif any(status == 'cancelled' for status in statuses):
            self.status = 'cancelled'
        else:
            self.status = 'pending'
        self.save()
    
class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('packaged', 'Packaged'),
        ('cancelled', 'Cancelled'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    toppings = models.ManyToManyField(Topping, through='ProductTopping')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} X {self.product.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.order.update_status()
    
class ProductTopping(models.Model):
    topping = models.ForeignKey(Topping, on_delete=models.SET_NULL, blank=True, null=True)
    cart_item = models.ForeignKey(CartItem, on_delete=models.SET_NULL, blank=True, null=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.SET_NULL, blank=True, null=True)
    
    def __str__(self) -> str:
        if self.cart_item:
            return f"{self.topping.name} for {self.cart_item.product.name}"
        elif self.order_item:
            return f"{self.topping.name} for {self.order_item.product.name}"
    
class Geography(models.Model):
    address = models.CharField(_("Exact Location"), max_length=300)
    phone_number = PhoneNumberField(_("Phone Number"), max_length=20, region="KE")
    
    class Meta:
        verbose_name_plural = "Geography"
    
    def __str__(self) -> str:
        return f"Selling point details"