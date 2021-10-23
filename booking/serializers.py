from rest_framework import serializers
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from .models import *




class RegisterSerializer(serializers.ModelSerializer):
    password=serializers.CharField(max_length=68,min_length=6,write_only=True)

    class Meta:
        model=User
        fields=['email','username','password']

    def validate(self, attrs):
        email = attrs.get('email','')
        username=attrs.get('username','')
        if not username.isalnum():
            raise serializers.ValidationError('The username should only contain alphanumeric characters')
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class EmailVerificationSerializer(serializers.ModelSerializer):
    token=serializers.CharField(max_length=555)
    class Meta:
        model=User
        fields=['token']
        

        
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls,user):
        token = super().get_token(user)
        token['username'] = user.username

        return token

class ResetPasswordEmailRequest(serializers.Serializer):
    email = serializers.EmailField(min_length=2)
    class Meta:
        fields = ['email']

class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=6, max_length=64, write_only= True)
    token = serializers.CharField(min_length=1, write_only= True)
    uidb64 = serializers.CharField(min_length=1, write_only= True)
    class Meta:
        fields = ['password', 'token','uidb64']
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The token is invalid', 401)
            user.set_password(password)
            user.save()
        except Exception as e:
            raise AuthenticationFailed('The token is invalid', 401)
        return super().validate(attrs)

# newwwwwwwww--------------------------------------------------------------------------
class PostSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('title', 'description','image', 'posted_on', 'user')
        model = Post
class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('id','customer','address','contact','orders','total_sale')
        model = Customer

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('id','name', 'course', 'status', 'price', 'image', 'num_order', 'content_description', 'location')
        model = Food

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('staff_id', 'address', 'contact', 'salary', 'role')
        model = Staff

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('id','customer', 'order_timestamp', 'delivery_timestamp', 'payment_status', 'delivery_status', 'if_cancelled', 'total_amount', 'payment_method', 'location', 'delivery_boy')
        model = Order

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('user','content')
        model = Comment

class DataSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('date','sales','expenses')
        model = Data

class OrderContentSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('food','order')
        model = OrderContent

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        fields =('id','image','amount','food','user')
        model = Cart

class DeliveryBoySerializer(serializers.ModelSerializer):
    class Meta:
        fields =('order','delivery_boy')
        model = DeliveryBoy 