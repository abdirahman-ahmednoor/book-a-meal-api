from django.shortcuts import render,redirect
from rest_framework import generics,status,views
from .serializers import *
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
import jwt
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import smart_str, force_str, smart_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework_simplejwt.views import TokenRefreshView
# Create your views here.
from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from . forms import PostForm
from django.core.files.storage import FileSystemStorage


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self,request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
         
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink=reverse('email-verify')
        absurl='http://'+current_site+relativeLink +"?token="+ str(token)
        email_body = 'Hi' + user.username + 'Use link below to verify your email\n' + 'domain' + absurl

        data = {'email_body': email_body, 'to_email': user.email,
                'email_subject': 'Verify your email'}


        Util.send_email(data) 
        return Response(user_data, status=status.HTTP_201_CREATED)

class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer
    
    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self,request):
        token = request.GET.get("token")
        try:
           payload = jwt.decode(token,settings.SECRET_KEY, algorithms=['HS256'])
           user = User.objects.get(id=payload['user_id'])
           if not user.is_verified:
                user.is_verified = True
                user.is_active = True
                user.save()
           return Response({'email':'Successfully activated'}, status=status.HTTP_200_OK)



        except jwt.ExpiredSignatureError as identifier:
            return Response({'error':'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.exceptions.DecodeError as identifier:
            return Response({'error':'Invlid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer


class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequest
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        email = request.data['email']
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse('password-reset-confirm',kwargs={'uidb64':uidb64, 'token': token})
            absolute_url = 'http://'+current_site+relativeLink
            email_body = 'Hello, \n Use the link below to reset password for your account \n' + absolute_url
            data = {'email_body': email_body, 'to_email': user.email, 'email_subject':'Password Reset'}
            Util.send_email(data)
        return Response({'success': 'We have sent a reset link in your email. Please check it out'}, status=status.HTTP_200_OK)
class PasswordTokenViewAPI(generics.GenericAPIView):
    serializer_class=CustomTokenObtainPairSerializer
    def get(self, request,uidb64,token):
        try:
            id=smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response({'error': 'Invalid Token. Request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'message': 'Credentials Valid', 'uidb64':uidb64, 'token': token}, status=status.HTTP_200_OK)
        except DjangoUnicodeDecodeError:
                return Response({'error': 'Invalid Token. Please request a new one'}, status=status.HTTP_401_UNAUTHORIZED)
class SetNewPasswordAPIView(generics.GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    def patch(self,request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'message':'Password reset successful'}, status=status.HTTP_200_OK)



# view -------------------------------------------------------------------------

@login_required
@staff_member_required
def dashboard_admin(request):
    comments = Comment.objects.count()
    orders = Order.objects.count()
    customers = Customer.objects.count()
    completed_orders = Order.objects.filter(payment_status="Completed")
    top_customers = Customer.objects.filter().order_by('-total_sale')
    latest_orders = Order.objects.filter().order_by('-order_timestamp')
    datas = Data.objects.filter().order_by('date')
    sales = 0
    for order in completed_orders:
        sales += order.total_amount

    context = {
        'comments':comments,
        'orders':orders,
        'customers':customers,
        'sales':sales,
        'top_customers': top_customers,
        'latest_orders':latest_orders,
        'datas':datas,
    }
    return render(request, 'admin_temp/index.html', context)

@login_required
@staff_member_required
def users_admin(request):
    customers = Customer.objects.filter()
    print(customers)
    return render(request, 'admin_temp/users.html', {'users':customers})

@login_required
@staff_member_required
def orders_admin(request):
    orders = Order.objects.filter()
    dBoys = Staff.objects.filter(role='Delivery Boy')
    print(dBoys)
    return render(request, 'admin_temp/orders.html', {'orders':orders, 'dBoys':dBoys})

@login_required
@staff_member_required
def foods_admin(request):
    foods = Food.objects.filter()
    return render(request, 'admin_temp/foods.html', {'foods':foods})

@login_required
@staff_member_required
def sales_admin(request):
    sales = Data.objects.filter()
    return render(request, 'admin_temp/sales.html', {'sales':sales})

def menu(request):
    cuisine = request.GET.get('cuisine')
    print(cuisine)
    if cuisine is not None:
        if ((cuisine == "Gujarati") or (cuisine == "Punjabi")):
            foods = Food.objects.filter(status="Enabled", course=cuisine)
        elif(cuisine == "south"):
            foods = Food.objects.filter(status="Enabled", course="South Indian")
        elif(cuisine == "fast"):
            foods = Food.objects.filter(course="Fast")
    else:
        foods = Food.objects.filter()
        return render(request, 'menu.html', {'foods':foods, 'cuisine':cuisine})


def index(request):
    food = Food.objects.filter().order_by('-num_order')
    return render(request, 'index.html', {'food':food})


@login_required
@staff_member_required
def confirm_order(request, orderID):
    order = Order.objects.get(id=orderID)
    order.confirmOrder()
    order.save()
    customerID = order.customer.id
    customer = Customer.objects.get(id=customerID)
    customer.total_sale += order.total_amount
    customer.orders += 1
    customer.save()
    return redirect('booking:orders_admin')

@login_required
@staff_member_required
def confirm_delivery(request, orderID):
    to_email = []
    order = Order.objects.get(id=orderID)
    order.confirmDelivery()
    order.save()
    mail_subject = 'Order Delivered successfully'
    to = str(order.customer.customer.email)
    to_email.append(to)
    from_email = 'abdirahman.noor09@gmail.com'
    message = "Hi "+order.customer.customer.first_name+" Your order was delivered successfully. Please go to your dashboard to see your order history. <br> Your order id is "+orderID+". Share ypour feedback woth us."
    send_mail(
        mail_subject,
        message,
        from_email,
        to_email,
    )
    return redirect('booking:orders_admin')

@login_required
@staff_member_required
def edit_food(request, foodID):
    food = Food.objects.filter(id=foodID)[0]
    if request.method == "POST":
        if request.POST['price'] != "":
            food.price = request.POST['price']
        
        # if request.POST['discount'] != "":
        #     food.discount = request.POST['discount'] 
        
        # food.sale_price = (100 - float(food.discount))*float(food.price)/100

        status = request.POST.get('disabled')
        print(status)
        if status == 'on':
            food.status = "Disabled"
        else:
            food.status = "Enabled"
        
        food.save()
    return redirect('booking:foods_admin')

@login_required
@staff_member_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        address = request.POST['address']
        contact = request.POST['contact']
        email = request.POST['email']
        password = request.POST['password']
        confirm_pass = request.POST['confirm_password']
        username = email.split('@')[0]
        
        if (first_name == "") or (last_name == "") or (address == "") or (contact == "") or (email == "") or (password == "") or (confirm_pass == ""):
            customers = Customer.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/users.html', {'users': customers, 'error_msg': error_msg})

        if password == confirm_pass:
            user = User.objects.create(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            user.save()
            cust = Customer.objects.create(customer=user, address=address, contact=contact)
            cust.save()
            success_msg = "New user successfully created"
            customers = Customer.objects.filter()
            return render(request, 'admin_temp/users.html', {'users': customers, 'success_msg': success_msg})

    return redirect('booking:users_admin')

@login_required
@staff_member_required
def add_food(request):
    if request.method == "POST":
        name = request.POST['name']
        course = request.POST['course']
        status = request.POST['status']
        content = request.POST['content']
        price = request.POST['base_price']
        image = request.FILES['image']
        location = request.POST['location']
        fs = FileSystemStorage()
        filename = fs.save(image.name, image)

        if (name == "") or (course is None) or (status is None) or (content == "") or (price == ""):
            foods = Food.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/foods.html', {'foods': foods, 'error_msg': error_msg})

        food = Food.objects.create(name=name, course=course, status=status, content_description=content, price=price, image=filename, location=location)
        food.save()
        foods = Food.objects.filter()
        success_msg = "Please enter valid details"
        return render(request, 'admin_temp/foods.html', {'foods': foods, 'success_msg': success_msg})
    return redirect('booking:foods_admin')

@login_required
@staff_member_required
def add_deliveryBoy(request, orderID):
    order = Order.objects.get(id=orderID)
    dName = request.POST['deliveryBoy']
    print(dName)
    user = User.objects.get(first_name=dName)
    deliveryBoy = Staff.objects.get(staff_id=user)
    order.delivery_boy = deliveryBoy
    order.save()
    return redirect('booking:orders_admin')

@login_required
@staff_member_required
def add_sales(request):
    if request.method == "POST":
        date = request.POST['date']
        sales = request.POST['sales']
        expenses = request.POST['expenses']
        
        if (date is None) or (sales == "") or (expenses == ""):
            sales = Data.objects.filter()
            error_msg = "Please enter valid details"
            return render(request, 'admin_temp/sales.html', {'sales': sales, 'error_msg': error_msg})

        data = Data.objects.create(date=date, sales=sales, expenses=expenses)
        data.save()
        datas = Data.objects.filter()
        success_msg = "Sales data added successfully!"
        return render(request, 'admin_temp/sales.html', {'sales': datas, 'success_msg': success_msg})

    return redirect('booking:foods_admin')

@login_required
@staff_member_required
def edit_sales(request, saleID):
    data = Data.objects.filter(id=saleID)[0]
    if request.method == "POST":
        if request.POST['sales'] != "":
            data.sales = request.POST['sales']
        
        if request.POST['expenses'] != "":
            data.expenses = request.POST['expenses'] 
        
        data.save()
    return redirect('booking:sales_admin')

@login_required
def food_details(request, foodID):
    food = Food.objects.get(id=foodID)
    return render(request, 'user/single.html', {'food':food})

@login_required
def addTocart(request, foodID, userID):
    food = Food.objects.get(id=foodID)
    user = User.objects.get(id=userID)
    cart = Cart.objects.create(food=food, user=user)
    cart.save()
    return redirect('booking:cart')

@login_required
def delete_item(request, ID):
    item = Cart.objects.get(id=ID)
    item.delete()
    return redirect('booking:cart')

@login_required
def cart(request):
    user = User.objects.get(id=request.user.id)
    items = Cart.objects.filter(user=user)
    total = 0
    for item in items:
        total += item.food.sale_price
    return render(request, 'cart.html', {'items': items, 'total':total})

@login_required
def placeOrder(request):
    to_email = []
    customer = Customer.objects.get(customer=request.user)
    print(customer.address)
    items = Cart.objects.filter(user=request.user)
    for item in items:
        food = item.food
        order = Order.objects.create(customer=customer, order_timestamp=timezone.now(), payment_status="Pending", 
        delivery_status="Pending", total_amount=food.sale_price, payment_method="Cash On Delivery", location=customer.address)
        order.save()
        orderContent = OrderContent(food=food, order=order)
        orderContent.save()
        item.delete()
    mail_subject = 'Order Placed successfully'
    to = str(customer.customer.email)
    to_email.append(to)
    from_email = 'abdirahman.noor09@gmail.com'
    message = "Hi "+customer.customer.first_name+" Your order was placed successfully. Please go to your dashboard to see your order history. <br> Your order id is "+Order.id+""
    send_mail(
        mail_subject,
        message,
        from_email,
        to_email,
    )
    return redirect('booking:cart')

@login_required
def my_orders(request):
    user = User.objects.get(id=request.user.id)
    customer = Customer.objects.filter(customer=user)
    orders = Order.objects.filter(customer=customer)
    return render(request, 'orders.html', {'orders': orders})

@login_required
def delivery_boy(request):
    user = User.objects.get(id=request.user.id)
    try:
        customer = Customer.objects.get(customer=user)
    except Customer.DoesNotExist:
        staff = Staff.objects.get(staff_id=user)
        if staff is None or staff.role != 'Delivery Boy':
            redirect('booking:index')
        else:
            orders = DeliveryBoy.objects.filter(delivery_boy=staff)
            return render(request, 'delivery_boy.html', {'orders':orders})
    
    return redirect('booking:index')
        
@login_required
def post(request):
  if request.method == 'POST':
    post_form = PostForm(request.POST,request.FILES) 
    if post_form.is_valid():
      new_post = post_form.save(commit = False)
      new_post.user = request.user
      new_post.save()
      return redirect('booking:index')

  else:
    post_form = PostForm()
  return render(request,'post.html',{"post_form":post_form})


# APIView

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

class CustomerList(generics.ListCreateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
class CustomerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

class OrderList(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class StaffList(generics.ListCreateAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
class StaffDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer    

class FoodList(generics.ListCreateAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
class FoodDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer

class CommentList(generics.ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer    

class DataList(generics.ListCreateAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer
class DataDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Data.objects.all()
    serializer_class = DataSerializer    

class OrderContentList(generics.ListCreateAPIView):
    queryset = OrderContent.objects.all()
    serializer_class = OrderContentSerializer
class OrderContentDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = OrderContent.objects.all()
    serializer_class = OrderContentSerializer   

class CartList(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
class CartDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer     

class DeliveryBoyList(generics.ListCreateAPIView):
    queryset = DeliveryBoy.objects.all()
    serializer_class = DeliveryBoySerializer
class DeliveryBoyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = DeliveryBoy.objects.all()
    serializer_class = DeliveryBoySerializer   