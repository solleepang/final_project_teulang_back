from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

User = get_user_model()

class UserRegisterationTestCase(APITestCase):
    def test_registration(self):
        url = reverse("sign_up_view")  # import reverse와 url name을 활용하면, 알아서, 해당되는 url을 가져옴. url의 변경이 와도 상관 없음.
        user_data = {
            "email":"john@t.com",
            "nickname":"john",
            "password":"johnpassword"
        }
        response = self.client.post(url, user_data, format='json') # client를 이용해 post를 보내고 url로 user_data를 담아 보내서 response를 받아온다.
        print(response.data)                                       # 출력값: .{'message': '회원가입이 완료되었습니다.'}
        self.assertEqual(response.status_code, 201)

    def test_registeration_password_validation(self):
        url = reverse("sign_up_view")
        user_data = {'email':'john@t.com',"nickname":"john", "password":"1234"}
        response = self.client.post(url, user_data, format='json')
        self.assertEquals(response.status_code, 400)