from django.urls import path
from users import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='sign_up_view'),
    path('signup-confirm/', views.DuplicateEmailConfirmView.as_view(), name='duplicate_email_confirm_view'),
    path('nickname-confirm/', views.DuplicateNicknameConfirmView.as_view(), name='duplicate_cnickname_onfirm_view'),
    path('verify-email//<str:uidb64>/<str:token>/', views.EmailVerificationView.as_view(), name='verify_email_view'),
    path('reset-password/', views.ResetPasswordView.as_view(), name="reset_password_view"),    # 3 이메일, 본인인증 코드, 새 비밀번호, 새 비밀번호 확인을 받아서 비밀번호 재설정
    path('reset-password-email/', views.ResetPasswordView.as_view(), name="reset_password_email_view"),   # 1 비밀번호 재발송을 위한 본인인증을 위한 코드를 담긴 이메일 발송
    path('verify-email-password/', views.EmailPasswordVerificationView.as_view(), name='verify_email_password_view'),  # 2 이메일과 사용자 입력 인증코드를 받아, 이메일에 담긴 인증코드와 사용자가 입력한 인증코드가 일치하는 확인
    path('login/', views.LoginView.as_view(), name='login_view'),
    path('api/signout/<int:user_id>/', views.UserUpdateView.as_view(), name='signout_view'), # 회원탈퇴 url
    path('<int:user_id>/',views.UserDetailView.as_view(), name='myprfile_view'), # 마이페이지 및 프로필 url
    path('userModify/<int:user_id>/', views.UserUpdateView.as_view(), name='update_view'), # 회원정보수정 url
    path('follow/<int:user_id>/', views.FollowView.as_view(), name='follow')
]
