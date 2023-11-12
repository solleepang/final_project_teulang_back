from django.urls import path
from users import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='sign_up_view'),
    path('signup-confirm/', views.DuplicateEmailConfirmView.as_view(), name='duplicate_email_confirm_view'),
    path('nickname-confirm/', views.DuplicateNicknameConfirmView.as_view(), name='duplicate_cnickname_onfirm_view'),
    path('verify-email/<str:uidb64>/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email_view'),
    path('login/', views.LoginView.as_view(), name='login_view'),
    path('api/signout/<int:user_id>/', views.UserUpdateView.as_view(), name='signout_view'), # 회원탈퇴 url
    path('<int:user_id>/',views.UserDetailView.as_view(), name='myprfile_view'), # 마이페이지 및 프로필 url
    path('userModify/<int:user_id>/', views.UserUpdateView.as_view(), name='update_view') # 회원정보수정 url
]
