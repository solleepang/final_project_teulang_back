from django.urls import path
from my_frige import views

urlpatterns = [
    path('<int:user_id>/myFrige/<int:ingredient_id>/',views.MyFrigeView.as_view(), name='my_frige_view'), # 내 냉장고 등록/조회
    path('<int:user_id>/myFrige/',views.MyFrigeView.as_view(), name='my_frige_view'), # 내 냉장고 수정/삭제
]