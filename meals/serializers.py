from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Category,Products,Profile,Cart,CartItem




class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={"input_type":"password"},write_only=True)

    class Meta:
        model = User
        fields = ["username","email","password","password2"]
        extra_kwargs = {'password':{"write_only":True}}

    def create(self,validated_data):
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        password2 = validated_data.pop('password2')

        if password != password2:
            raise serializers.ValidationError({"password":"Password must match"})

        user = User(username=username,email=email)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type":"password"},write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(request=self.context.get('request'), username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid username or password")

        else:
            raise serializers.ValidationError("Must include both username and password")

        data['user'] = user
        return data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user','phone','street','home','kvartira')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'



class ProductSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    class Meta:
        model = Products
        fields = "__all__"










class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product',  'quantity']

        extra_kwargs = {
            'cart': {'read_only': True},
        }

        def get_price(self, obj):
            return obj.get_price()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True,read_only=True)
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Cart
        fields = ['id', 'user', 'ordered', 'total_price', 'items']

    def create(self,validated_data):
        items_data = self.context['request'].data.get('items', [])
        cart = super().create(validated_data)
        for item_data in items_data:
            CartItem.objects.create(cart=cart, **item_data)
        return cart

