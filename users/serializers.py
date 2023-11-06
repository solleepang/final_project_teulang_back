from rest_framework import serializers
from users.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import get_object_or_404

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import check_password

class UserSerializer(serializers.ModelSerializer):
    '''회원가입시 사용자가 보내는 JSON 형태의 데이터를 역직렬화하여 모델 객체 형태의 데이터를 생성하기 위한 Serializer 입니다. '''

    # 이메일 중복 확인 에러 메세지 커스텀
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="이미 존재하는 이메일입니다.")]
                    #EmailValidator(queryset=User.objects.all(), message="이메일 형식이 올바르지 않습니다.")] # 이메일 유효성검사는 TypeError: EmailValidator.__init__() got an unexpected keyword argument 'queryset' 에러 발생
    )
    # 닉네임 중복 확인 에러 메세지 커스텀
    nickname = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="이미 존재하는 닉네임입니다.")]
    )
    password = serializers.CharField(write_only=True, required=True)
    # password_check = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "nickname", "password")  # , "password_check"
        extra_kwargs = {'password': {'write_only': True}}

    # 비밀번호 두 개 맞는지 체크
    # def validate_password_check(self, attrs):
    #     print(attrs) # 번갈아서 출력됨. 처음엔 password 나오다가, password_check만 계속 나옴.
        # password = attrs[password]
        # password_check = attrs[password_check]
        # if password != password_check:
        #     raise ValidationError("비밀번호를 확인해 주세요")
        # return attrs.email

    def create(self, validated_data):
        """회원가입을 위한 메서드입니다."""
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user



class LoginSerializer(TokenObtainPairSerializer):
    '''로그인시 생성되는 토큰의 payload를 커스텀하기 위한 Serializer입니다.'''

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['user_id'] = user.id
        token['email'] = user.email
        token['nickname'] = user.nickname
        token['user_img'] = user.user_img.url

        return token