from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name







class Products(models.Model):
    category = models.ForeignKey(Category,related_name="products",on_delete=models.CASCADE)
    name = models.CharField("name",max_length=200)
    old_price = models.IntegerField(default=0,blank=True)
    price = models.IntegerField(default=0)
    desc = models.TextField()
    image = models.ImageField(upload_to="image/products",blank=True,null=True)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.ForeignKey(User,related_name="profile",on_delete=models.CASCADE)
    phone = models.CharField(max_length=50)
    street = models.CharField(max_length=100,null=True,blank=True)
    home = models.CharField(max_length=100,null=True,blank=True)
    kvartira = models.CharField(max_length=50,null=True,blank=True)

class Cart(models.Model):
    user = models.ForeignKey(User,related_name="orders",on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    total_price = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    date = models.DateTimeField(auto_now_add=True)

    def calculate_total_price(self):
        self.total_price = sum(item.get_price() * item.quantity for item in self.items.all())
        self.save()


    def __str__(self):
        return f"{self.user.username} - ${self.total_price:.2f}"






class CartItem(models.Model):
    cart = models.ForeignKey(Cart,related_name="items",on_delete=models.CASCADE)
    product = models.ForeignKey(Products, related_name="cart_items", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def get_price(self):
        return self.product.price

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_cart_total()

    def update_cart_total(self):
        cart = self.cart
        total_price = sum(item.get_price() * item.quantity for item in cart.items.all())
        cart.total_price = total_price
        cart.save()

    def __str__(self):
        return f"{self.cart.user.username} - {self.product.name} ({self.quantity})"



