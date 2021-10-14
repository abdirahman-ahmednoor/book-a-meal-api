from django.urls import path
from .views import *
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    path('register', RegisterView.as_view(),name = 'register'),
    path('login', LoginAPIView.as_view(),name = 'login'),
    path('email-verify/', VerifyEmail.as_view(),name = 'email-verify'),
    path('reset-email-request/', RequestPasswordResetEmail.as_view(), name="reset-email-request"),
    path('password-reset/<uidb64>/<token>/', PasswordTokenViewAPI.as_view(), name="password-reset-confirm"),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name="password-reset-complete"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

      # APIViews
    path('<int:pk>/', PostDetail.as_view()),
    path('post/', PostList.as_view()),

    path('<int:pk>/', CustomerDetail.as_view()),
    path('customer/', CustomerList.as_view()),

    path('<int:pk>/', StaffDetail.as_view()),
    path('staff/v1', StaffList.as_view()),

    path('<int:pk>/', OrderDetail.as_view()),
    path('order', OrderList.as_view()),

    path('<int:pk>/', FoodDetail.as_view()),
    path('food/v1', FoodList.as_view()),

    path('<int:pk>/', CartDetail.as_view()),
    path('cart', CartList.as_view()),

    path('<int:pk>/', CommentDetail.as_view()),
    path('comment', CommentList.as_view()),

    path('<int:pk>/', DataDetail.as_view()),
    path('data', DataList.as_view()),

    path('<int:pk>/', DeliveryBoyDetail.as_view()),
    path('deliveryboy', DeliveryBoyList.as_view()),

    path('<int:pk>/', OrderContentDetail.as_view()),
    path('ordercontent', OrderContentList.as_view()),

]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)