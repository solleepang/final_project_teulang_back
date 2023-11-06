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


    # 이메일 유효성과 중복 확인 에러 메세지 커스텀
    def validate_email(self, obj):
        if email.is_valid(obj):
            return obj
        elif email.UniqueValidator():   # 이메일 중복 에러 메세지
            raise ValidationError("이미 존재하는 이메일입니다.")
        raise serializers.ValidationError('메일 형식이 올바르지 않습니다.')

    # 닉네임 중복 확인 에러 메세지 커스텀
    def validate_nickname(self, obj):
        if nickname_isvalid(obj):
            return obj
        elif nickname.UniqueValidator():   # 닉네임 중복 에러 메세지
            raise ValidationError("이미 존재하는 이메일입니다.")
        raise serializers.ValidationError('닉네임은 한 글자 이상이어야 합니다.')
            
    # 비밀번호 에러 메세지 커스텀
    def validate_password(self, obj):
        if password_isvalid(obj):
            return hash_password(obj)
        raise serializers.ValidationError("비밀번호는 8 자리 이상이어야 합니다.")
    
    class Meta:
        model = User
        fields =("email", "nickname", "password")
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {
                'validators': [UniqueValidator(queryset=User.object.all())]
            },
            'email': {
                'validators': [UniqueValidator(queryset=User.object.all())]
            },
        }

    


    '''1. serializer - validate_email(커스텀/정규식) 2. orm is_exe'''
    # 유효한 이메일인지 확인
    # email = serializers.EmailField(required=True, validator=[EmailValidator]) # (message="유효하지 않은 이메일입니다.")
    # 이메일 중복 확인
    # email = serializers.EmailField(max_length=255, required=True, validators=[UniqueValidator(message=("이미 존재하는 이메일 입니다"))]) # 이게 없어도 어떻게 오류메세지를 나는지 확인
    
    # 닉네임 중복 확인
    # nickname = serializers.CharField(required=True, validator =[UniqueValidator(message=("이미 존재하는 닉네임입니다."))])
    
    # # 비밀번호 해싱 및 확인(2개 )
    # password = serializers.CharField(write_only=True,required=True,validators=[validate_password])
    # password_check = serializers.CharField(required=True, validators=[PasswordValidator()])
    
    # def validate_password_check(self, attrs):
    #     password = attrs['password']
    #     password_check = attrs['password_check']
    #     if password != password_check:
    #         raise ValidationError("비밀번호를 확인해 주세요")
    #     return username
    
    class Meta:
        model = User
        fields =("email", "nickname", "password")


    def create(self, validated_data):
        """회원가입을 위한 메서드입니다."""
        user = super().create(validated_data)
        password = user.password
        user.set_password(password)
        user.save()
        return user
    
    def update(self, obj, validated_data):
        # password hashing
        if 'password' in validated_data:
            password = validated_data.pop('password')
            obj.set_password(password)
        
        email = obj.email   # 프론트 단에서 email 받지 못하게끔 설정 필요. 설정 시 삭제 가능한 부분.
        
        for key, value in validated_data.items():
            setattr(obj, key, value)
        
        # 프론트 단에서 email 받지 못하게끔 설정 필요. 설정 시 삭제 가능한 부분.
        setattr(obj, 'email', email)
        obj.save()
        return obj


class LoginSerializer(TokenObtainPairSerializer):
    '''로그인시 생성되는 토큰의 payload를 커스텀하기 위한 Serializer입니다.'''

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['nickname'] = user.nickname
        token['user_img'] = user.user_img.url

        return token