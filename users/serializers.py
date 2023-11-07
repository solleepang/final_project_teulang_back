from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import get_object_or_404

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import check_password

from rest_framework.exceptions import AuthenticationFailed, NotFound
import re   # 로그인 시 이메일 주소 유효성 검사를 위함.

class UserSerializer(serializers.ModelSerializer):
    '''회원가입시 사용자가 보내는 JSON 형태의 데이터를 역직렬화하고, 유효성 검사를 거쳐 모델 객체 형태의 데이터를 생성하기 위한 Serializer 입니다. '''

    # 이메일 중복 확인 에러 메세지 커스텀
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="이미 존재하는 이메일입니다.")
                    ,EmailValidator(message="이메일 형식이 올바르지 않습니다.")] # 231107/19:36 오류메세지 2개 뜸 "이메일 형식이 올바르지 않습니다.", "유효한 이메일 주소를 입력하십시오." | 이전: 이메일 유효성검사는 TypeError: EmailValidator.__init__() got an unexpected keyword argument 'queryset' 에러 발생 | 이메일 필드 임포트해도 똑같은 오류 발생
    )
    # 닉네임 중복 확인 에러 메세지 커스텀
    nickname = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="이미 존재하는 닉네임입니다.")]
    )
    password = serializers.CharField(write_only=True, required=True)
    password_check = serializers.CharField(style={'input_type':'password'}, write_only=True)

    class Meta:
        model = User
        fields = ("email", "nickname", "password", "password_check")
        extra_kwargs = {'password': {'write_only': True}}

    # 비밀번호 유효성 검사와 비밀번호와 확인 비밀번호 일치 확인
    def validate(self, attrs):
        password = attrs.get('password')
        password_check =attrs.pop('password_check')
        try:
            validate_password(password=password)
        except ValidationError as err:
            raise serializers.ValidationError({'password':err.messages})
        if password != password_check:
                raise ValidationError("비밀번호와 확인 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
        return attrs

    def create(self, validated_data):
        """회원가입을 위한 메서드입니다."""
        user = super().create(validated_data)
        user.set_password(user.password)
        user.save()
        return user



class LoginSerializer(TokenObtainPairSerializer):
    '''로그인 실패 시 error 메세지를 커스텀하고,  생성되는 토큰의 payload를 커스텀하기 위한 Serializer입니다.'''

    def validate(self, attrs):
        user = get_object_or_404(User, email=attrs[self.username_field])

        # (미구현) 속도 느려지는 이슈로 주석 처리, 이메일 형식이 유효하지 않을 때 에러 메세지
        # def is_email_valid(email):
        #     REGEX_EMAIL = '([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
        #     if not re.fullmatch(REGEX_EMAIL, email):
        #         return "이메일 형식을 확인하세요."
        # print(email)
        # is_email_valid(attrs['email'])

        # 전달받은 비밀번호와 사용자의 비밀번호를 비교해 검증하고, 커스텀한 에러 메세지 보내기
        if check_password(attrs['password'], user.password) == False:
            raise AuthenticationFailed("사용자를 찾을 수 없습니다. 로그인 정보를 확인하세요.") # password 정보만 틀렸을 때
        data = super().validate(attrs)
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = user.id
        token['email'] = user.email
        token['nickname'] = user.nickname
        token['user_img'] = user.user_img.url

        return token