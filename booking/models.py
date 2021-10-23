from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from django.contrib.auth.models import(
    AbstractBaseUser,BaseUserManager,PermissionsMixin)
from rest_framework_simplejwt.tokens import RefreshToken
from cloudinary.models import CloudinaryField
from .models import *
class UserManager(BaseUserManager):
    def create_user(self,username,email,password=None):
        if username is None:
            raise TypeError('User should have a username')
        if email is None:
            raise TypeError('User should have an Email')
        user=self.model(username=username,email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user
        
    def create_superuser(self,username,email,password=None):
        if password is None:
            raise TypeError('Password should not be none')
        user=self.create_user(username,email,password)
        user.is_superuser=True
        user.is_staff=True
        user.save()
        return user

class User(AbstractBaseUser,PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.
    Username and password are required. Other fields are optional.
    """
    username = models.CharField(max_length=255,unique=True,db_index=True ) 
    email = models.EmailField(max_length=255,unique=True,db_index=True )
    is_verified = models.BooleanField(default=True)
    is_active = models.BooleanField(default = True)
    created_at =models.DateTimeField(auto_now_add =True)
    updated_at = models.DateTimeField(auto_now =True)
    is_staff = models.BooleanField(
        ('staff status'),
        default=False,
        help_text=('Designates whether the user can log into this admin site.'),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects  = UserManager()   

    def __str__(self):
        return self.email


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }

# newwwwwwwwwwwwwww----------------------------------------------------
class Customer(models.Model):
    pending = 'Pending'
    verified = 'Verified'

    STATUS = (
        (pending,pending),
        (verified,verified),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    contact = models.CharField(max_length = 10)
    orders = models.IntegerField(default=0)
    total_sale = models.IntegerField(default=0)

    def __str__(self):
        return self.customer

class Staff(models.Model):
    admin = 'Admin'
    deliveryboy = 'Delivery Boy'
    chef = 'Chef'

    ROLES = (
        (admin,admin),
        (chef,chef),
        (deliveryboy,deliveryboy),
    )
    
    staff_id = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField()
    contact = models.CharField(max_length = 10)
    email = User.email
    salary = models.IntegerField()
    role = models.CharField(max_length = 30, choices = ROLES)
    
    def __str__(self):
        return self.staff_id

class Order(models.Model):
    pending = 'Pending'
    completed = 'Completed'

    STATUS = (
        (pending,pending),
        (completed,completed),
    )

    cod = 'Cash On Delivery'
    card = 'Card Payment'
    upi = 'UPI Payment'

    PAYMENT = (
        (cod,cod),
        (card,card),
        (upi,upi),
    )

    pickup = 'PickUp'
    delivery = 'Delivery'

    TYPE = (
        (pickup, pickup),
        (delivery, delivery),
    )

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    order_timestamp = models.CharField(max_length=100, blank=True)
    delivery_timestamp = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length = 100, choices = STATUS)
    delivery_status = models.CharField(max_length = 100, choices = STATUS)
    if_cancelled = models.BooleanField(default = False)
    total_amount = models.IntegerField()
    payment_method = models.CharField(max_length = 100, choices = PAYMENT)
    location = models.CharField(max_length=200, blank=True, null=True)
    delivery_boy = models.ForeignKey(Staff,on_delete=models.CASCADE, null=True, blank=True)

    def confirmOrder(self):
        self.order_timestamp = timezone.localtime().__str__()[:19]
        self.payment_status = self.completed
        self.save()

    def confirmDelivery(self):
        self.delivery_timestamp = timezone.localtime().__str__()[:19]
        self.delivery_status = self.completed
        self.save()
    
    def __str__(self):
        return self.customer.__str__()

class Food(models.Model):
    indian = 'Indian Food'
    south = 'South Food'
    gujarati = 'Gujarati Food'
    punjabi = 'PunjabiFood'
    fast = 'Food'
    
    COURSE = (
        (indian,indian),
        (south,south),
        (gujarati,gujarati),
        (punjabi,punjabi),
        (fast,fast),
    )

    disabled = 'Disabled'
    enabled = 'Enabled'

    STATUS = (
        (disabled, disabled),
        (enabled, enabled),
    )
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250)
    course = models.CharField(max_length = 50, choices = COURSE)
    status = models.CharField(max_length=50, choices=STATUS)
    content_description = models.TextField()
    price = models.FloatField()
    image =CloudinaryField('image')
    location = models.CharField(max_length=200, blank=True, null=True)
    num_order = models.IntegerField(default=0)

    def __str__(self):
        return self.name
    
    #def calculateSalePrice(self):
     #   self.sale_price = (100.0 - self.discount)/100.0 * self.base_price
    

class Comment(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    content = models.CharField(max_length=250)

class Data(models.Model):
    date = models.DateField()
    sales = models.IntegerField()
    expenses = models.IntegerField()

class OrderContent(models.Model):
    quantity = models.IntegerField(default=1)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    image = CloudinaryField('image')
    amount = models.IntegerField(default=1)
    quantity = models.IntegerField(default=1)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class DeliveryBoy(models.Model):
    order= models.ForeignKey(Order, on_delete=models.CASCADE)
    delivery_boy = models.ForeignKey(Staff, on_delete=models.CASCADE)

class Post(models.Model):
  title = models.CharField(max_length=144)
  description = models.TextField()
  image = models.ImageField('image')
  posted_on = models.DateTimeField(auto_now_add=True)
  user = models.ForeignKey(User,on_delete = models.CASCADE)
  

  @classmethod
  def display_postt(cls):
    projects = cls.objects.all().order_by('-posted_on')
    return projects

  def save_post(self):
    self.save()

  def delete_post(self):
    self.delete()

  @classmethod
  def search_post(cls, title):
    return cls.objects.filter(title__icontains=title).all()

  @classmethod
  def get_post(cls):
    return cls.objects.all()

  def __str__(self):
    return f'{self.title}'


