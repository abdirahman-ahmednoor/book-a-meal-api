from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('cart/', views.cart, name='cart'),
    path('menu/', views.menu, name='menu'),
    path('myorders/', views.my_orders, name='my_orders'),
    
    path('dashboard/admin/users/', views.users_admin, name='users_admin'),
    path('dashboard/admin/orders/', views.orders_admin, name='orders_admin'),
    path('dashboard/admin/foods/', views.foods_admin, name='foods_admin'),
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/admin/sales/', views.sales_admin, name='sales_admin'),
    
    path('dashboard/admin/users/add_user/', views.add_user, name='add_user'),
    path('dashboard/admin/foods/add_food/', views.add_food, name='add_food'),
    path('dashboard/admin/sales/add_sales/', views.add_sales, name='add_sales'),
    path('dashboard/admin/foods/editFood/(?P<foodID>\d+)/', views.edit_food, name='edit_food'),
    path('dashboard/admin/foods/foodDetails/(?P<foodID>\d+)/', views.food_details, name='food_details'),
    path('dashboard/admin/sales/editSale/(?P<saleID>\d+)/', views.edit_sales, name='edit_sales'),
    
    path('dashboard/admin/orders/confirm_order/(?P<orderID>\d+)/', views.confirm_order, name='confirm_order'),
    path('dashboard/admin/orders/confirm_delivery/(?P<orderID>\d+)/', views.confirm_delivery, name='confirm_delivery'),
    
    path('delete_item/(?P<ID>\d+)/', views.delete_item, name='delete_item'),
    path('add_deliveryBoy/(?P<orderID>\d+)/', views.add_deliveryBoy, name='add_deliveryBoy'),
    path('placeOrder/', views.placeOrder, name='placeOrder'),
    path('addTocart/(?P<foodID>\d+)/(?P<userID>\d+)/', views.addTocart, name='addTocart'),
    path('post/',views.post,name='post'),
    path('dashboard/delivery_boy/', views.delivery_boy, name='delivery_boy'),

    path('<int:pk>/', PostDetail.as_view()),
    path('post/v1', PostList.as_view()),

    path('<int:pk>/', CustomerDetail.as_view()),
    path('customer/v1', CustomerList.as_view()),

    path('<int:pk>/', StaffDetail.as_view()),
    path('staff/v1', StaffList.as_view()),

    path('<int:pk>/', OrderDetail.as_view()),
    path('order/v1', OrderList.as_view()),

    path('<int:pk>/', FoodDetail.as_view()),
    path('food/v1', FoodList.as_view()),

    path('<int:pk>/', CartDetail.as_view()),
    path('cart/v1', CartList.as_view()),

    path('<int:pk>/', CommentDetail.as_view()),
    path('comment/v1', CommentList.as_view()),

    path('<int:pk>/', DataDetail.as_view()),
    path('data/v1', DataList.as_view()),

    path('<int:pk>/', DeliveryBoyDetail.as_view()),
    path('deliveryboy/v1', DeliveryBoyList.as_view()),

    path('<int:pk>/', OrderContentDetail.as_view()),
    path('ordercontent/v1', OrderContentList.as_view()),

]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
