from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

User = get_user_model()

class UserRegisterationTestCase(APITestCase):
    def setUp(self):
        self.data = {'email': 'john@t.com','nickname':'john', 'password':'johnpassword'}
        self.user = User.objects.create_user('john@mx.com', 'john','johnpassword')

    # 회원가입 테스트
    def test_registration(self):
        url = reverse("sign_up_view")  # import reverse와 url name을 활용하면, 알아서, 해당되는 url을 가져옴. url의 변경이 와도 상관 없음.
        user_data = {
            "email":"john1@t.com",
            "nickname":"john1",
            "password":"johnpassword1"
        }
        response = self.client.post(url, user_data, format='json') # client를 이용해 post를 보내고 url로 user_data를 담아 보내서 response를 받아온다.
        print(response.data)                                       # 출력값: .{'message': '회원가입이 완료되었습니다.'}
        self.assertEqual(response.status_code, 201)

    # 회원가입 이메일 유효성 검사 테스트
    def test_registeration_email_validation(self):
        url = reverse("sign_up_view")
        user_data = {'email':'john@t',"nickname":"john", "password":"1234t123!"}
        response = self.client.post(url, user_data, format='json')
        print(response.data)    # F{'email': [ErrorDetail(string='Enter a valid email address.', code='invalid')]}
        self.assertEquals(response.status_code, 400)

    # (미완)회원가입 이메일 중복 검사 테스트
    def test_registeration_email_duplicate_check(self):
        url = reverse("sign_up_view")
        user_data = {'email':'john@t.com',"nickname":"john1", "password":"1234t123!"}
        response = self.client.post(url, user_data, format='json')
        print(response.data)    # AssertionError: 201 != 400
        self.assertEquals(response.status_code, 400)

    # (미완)회원가입 닉네임 중복 검사 테스트
    def test_registeration_nickname_duplicate_check(self):
        url = reverse("sign_up_view")
        user_data = {'email':'john1@t.com',"nickname":"john", "password":"1234t123!"}
        response = self.client.post(url, user_data, format='json')
        print(response.data)    # # AssertionError: 201 != 400
        self.assertEquals(response.status_code, 400)

    # 회원가입 시 비밀번호 유효성 검사
    def test_registeration_password_validation(self):
        url = reverse("sign_up_view")
        user_data = {'email':'john11@t.com',"nickname":"john11", "password":"1234"}
        response = self.client.post(url, user_data, format='json')
        print(response.data)    # F {'password': [ErrorDetail(string='This password is too short. It must contain at least 8 characters.', code='invalid'), ErrorDetail(string='This password is too common.', code='invalid'), ErrorDetail(string='This password is entirely numeric.', code='invalid')]}
        self.assertEquals(response.status_code, 400)