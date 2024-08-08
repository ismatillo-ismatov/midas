import stripe
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework import viewsets,status,generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authtoken.models import Token
from rest_framework import permissions
from .models import Category,Products,Profile,Cart,CartItem
from .permissions import IsAdminOrReadOnly,IsOwnerProfile,IsOwnerCart
from .serializers import CategorySerializer,ProductSerializer,RegisterSerializer,LoginSerializer,ProfileSerializer,CartSerializer,CartItemSerializer

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY





def success_view(request):
    return render({request:"success"})
@api_view(['POST'])
@csrf_exempt
def create_checkout_session(request):
    try:
        DOMAIN = "http://localhost:8000"

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data':{
                        'currency':'usd',
                        'product_data':{
                            'name':'t-shirt',
                        },
                        'unit_amount': 500,
                    },
                    'quantity':1,
                }
            ],
            mode='payment',
            success_url=DOMAIN + '/success/',
            cancel_url=DOMAIN + '/cancel',

        )
        return JsonResponse({'id':checkout_session.id,'url': checkout_session.url})
    except Exception as e:
        return JsonResponse({'error':str(e)},status=500)
@api_view(['GET'])
@csrf_exempt
def payment_success(request):
    return JsonResponse({'status': 'success', 'message': 'Payment successful!'})

@api_view(['GET'])
@csrf_exempt
def payment_cancel(request):
    return JsonResponse({'status': 'cancel', 'message': 'Payment canceled!'})


class CreateCheckoutSessionView(APIView):
    def post(self,request,*args,**kwargs):
        user = request.user
        cart = Cart.objects.get(user=user,ordered=False)
        cart_items = CartItem.objects.filter(cart=cart)

        line_items = []
        for item in cart_items:
            line_items.append({
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        "name":item.product.name,
                    },
                    'unit_amount': int(item.product.price * 100),

                },
                'quantity':item.quantity,

            })

        checkout_session = stripe.checkout.Session.Create(
            payment_method_type = ['card'],
            line_items=line_items,
            mode='payment',
            succuss_url='http://localhost:8000/success/',
            cancel_url='http://localhost:8000/cancel/',

        )
        return  Response({'id':checkout_session.id})


class StripeWebhookView(APIView):
    def post(self,request,*args,**kwargs):
        payload = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
        endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

        try:
            event = stripe.Webhook.construct_event(
                payload,sig_header,endpoint_secret
            )
        except ValueError as e:
            return JsonResponse({'error':str(e)},status=400)
        except stripe.error.SignatureVerificationError as e:
            return JsonResponse({'error':str(e)},status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            cart = Cart.objects.get(user=request.user,ordered=False)
            cart.ordered = True
            cart.save()

            return  JsonResponse({'status':'success'},status=200)



class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self,request,*args,**kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"User created successfully"},status=status.HTTP_201_CREATED)
        return Response(serializer.error,status=status.HTTP_400_BAD_REQUEST)



class LoginView(APIView):
    def post(self,request,*args,**kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token,created = Token.objects.get_or_create(user=user)
            return Response({"token":token.key},status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



class ProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwnerProfile]

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)




class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]




class CartView(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,IsOwnerProfile]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        return Cart.objects.none()


class CartItemAPIView(APIView):
    def get(self,request,pk=None):
        user = request.user
        cart, _= Cart.objects.get_or_create(user=user,ordered=False)
        items = CartItem.Objects.filter(cart=cart)

        serializer = CartItemSerializer(items,many=True)
        return Response(serializer.data)

    def post(self,request,pk=None):
        user = request.user
        cart,_=Cart.objects.get_or_create(user=user,ordered=False)
        serializer =  CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(cart=cart)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return  Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def put(self,request,pk=None):
        try:
            item = CartItem.objects.get(pk=pk,cart__user=request.user)
            serializer = CartItemSerializer(item,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({"detail": "No CartItem matches the given query."},status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk=None):
        try:
            item = CartItem.objects.get(pk=pk, cart__user=request.user)
            serializer = CartItemSerializer(item, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except CartItem.DoesNotExist:
            return Response({"detail": "No CartItem matches the given query."}, status=status.HTTP_404_NOT_FOUND)



    def delete(self,request,pk=None):
        try:
            item = CartItem.objects.get(pk=pk,cart__user=request.user)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except CartItem.DoesNotExist:
            return Response({"detail": "No CartItem matches the given query."},status=status.HTTP_404_NOT_FOUND)



#