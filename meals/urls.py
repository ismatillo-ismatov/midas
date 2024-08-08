from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet,ProductViewSet,RegisterView,LoginView,ProfileView,CartView,CartItemAPIView,create_checkout_session,StripeWebhookView,payment_success,payment_cancel


router = DefaultRouter()
router.register(r'categoties',CategoryViewSet)
router.register(r"products",ProductViewSet)
router.register(r'profile',ProfileView)
router.register(r'carts',CartView,basename="cart"),

urlpatterns = [
    path('', include(router.urls)),
    path('register/',RegisterView.as_view(),name='register'),
    path('login/',LoginView.as_view(),name="login"),
    path('cart-items/',CartItemAPIView.as_view(),name="cart-item-list"),
    path('cart-items/<int:pk>/',CartItemAPIView.as_view(),name="cart-items-detail"),
    path('create-checkout-session/',create_checkout_session, name='create-checkout-session'),
    path('stripe-webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('success/', payment_success, name='payment-success'),
    path('cancel/', payment_cancel, name='payment-cancel'),

]