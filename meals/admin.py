from django.contrib import admin
from .models import Category,Products,Profile,Cart,CartItem
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
class CustomUserAdmin(UserAdmin):
    list_display = ('id','username', 'email', 'first_name', 'last_name', 'is_staff')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone','street',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id',"name")

@admin.register(Products)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','category','name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id","user", 'ordered', 'total_price', 'date')

@admin.register(CartItem)
class CartItem(admin.ModelAdmin):
    list_display = ('id','cart','product','quantity')
