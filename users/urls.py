from django.urls import path
from users import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='sign_up_view'),
    path('login/', views.LoginView.as_view(), name='login_view'),
]
