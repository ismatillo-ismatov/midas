from rest_framework import permissions
from .models import Cart
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_staff



class IsOwnerProfile(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsOwnerCart(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        cart = obj.cart
        return cart.user == request.user