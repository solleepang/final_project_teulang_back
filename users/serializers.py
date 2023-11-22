from rest_framework import serializers
from users.models import User
from articles.models import ArticleRecipe, RecipeBookmark

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.generics import get_object_or_404

from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.contrib.auth.hashers import check_password

from rest_framework.exceptions import AuthenticationFailed, NotFound
from users.validators import contains_special_character, contains_uppercase_letter, contains_lowercase_letter, contains_number

class ResetPasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(write_only=True, required=True)
    new_password_check = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ("new_password", "new_password_check")
        extra_kwargs = {'password': {'write_only': True}}


    # 비밀번호의 유효성검사
    def validate(self, value):
        password = value.get('new_password')
        password_check = value.pop('new_password_check')

        # 새로운 비밀번호 유효성 검사
        try:
            validate_password(password=password)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        # 새로운 비밀번호와 비밀번호 확인 일치 여부 확인
        if password != password_check:
            raise ValidationError("비밀번호와 확인 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")

        # 비밀번호 8자 이상, 문자/숫자/특수문자 포함 조건
        if (len(password) < 8
            or not (contains_uppercase_letter(password) or contains_lowercase_letter(password))
            or not contains_number(password)
            or not contains_special_character(password)):
            raise serializers.ValidationError("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다.") # 400 non_field_errors

        return value


    def update(self, instance, validated_data):
        """비밀번호 재설정을 위한 메서드입니다."""

        password = validated_data.pop("new_password")

        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    '''회원가입시 사용자가 보내는 JSON 형태의 데이터를 역직렬화하고, 유효성 검사를 거쳐 모델 객체 형태의 데이터를 생성하기 위한 Serializer 입니다. '''

    # 이메일 중복 확인 에러 메세지 커스텀
    email = serializers.EmailField(
        required=True,
        # 231107/19:36 오류메세지 2개 뜸 "이메일 형식이 올바르지 않습니다.", "유효한 이메일 주소를 입력하십시오."
        validators=[UniqueValidator(queryset=User.objects.all(
        ), message="이미 존재하는 이메일입니다."), EmailValidator(message="이메일 형식이 올바르지 않습니다.")]
    )
    # 닉네임 중복 확인 에러 메세지 커스텀
    nickname = serializers.CharField(
        required=True,
        validators=[UniqueValidator(
            queryset=User.objects.all(), message="이미 존재하는 닉네임입니다.")]
    )
    password = serializers.CharField(write_only=True, required=True)
    password_check = serializers.CharField(
        style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ("email", "nickname", "password", "password_check","following")
        extra_kwargs = {'password': {'write_only': True}}

    # 비밀번호 유효성 검사와 비밀번호와 확인 비밀번호 일치 확인
    def validate(self, attrs):
        password = attrs.get('password')
        password_check = attrs.pop('password_check')
        try:
            validate_password(password=password)
        except ValidationError as err:
            raise serializers.ValidationError({'password': err.messages})
        if password != password_check:
            raise ValidationError("비밀번호와 확인 비밀번호가 일치하지 않습니다. 다시 입력해주세요.")
        # 8
        if (len(password) < 8
            or not (contains_uppercase_letter(password) or contains_lowercase_letter(password))
            or not contains_number(password)
            or not contains_special_character(password)):
            raise serializers.ValidationError("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다.") # 400 non_field_errors
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

        # 사용자의 정보를 찾을 수 없을 때 404 에러 뱉어냄
        user = get_object_or_404(User, email=attrs['email'])

        # 전달받은 데이터와 사용자의 데이터의 이메일/비밀번호를 비교해 검증하고, 커스텀한 에러 메세지 보내기
        if user.is_active == False:
            raise AuthenticationFailed("이메일 인증이 필요합니다. 회원 가입시 이용한 이메일을 확인해주세요.")
        elif attrs['email'] != user.email:
            raise AuthenticationFailed("로그인에 실패했습니다. 로그인 정보를 확인하세요.") # 이메일 틀렸을 때
        elif check_password(attrs['password'], user.password) == False:
            raise AuthenticationFailed("로그인에 실패했습니다. 로그인 정보를 확인하세요.")  # 비밀번호 틀렸을 때
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


# 마이페이지에서 해당 작성자가 쓴 글을 받기 위한 클래스입니다.
class ArticleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipe
        fields = "__all__"
        
# 마이페이지에서 북마크한 글의 정보를 받기 위한 클래스입니다.      
class BookmarkRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipe
        # fields = "__all__"
        fields = ['author','title','description','recipe_thumbnail','recipe_thumbnail_api','api_recipe']

# 팔로잉 한 유저의 정보를 알기 위한 클래스입니다.
class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']

# 팔로우 한 유저의 정보를 알기 위한 클래스입니다.
class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'nickname']




class RecipeBookmarkSerializer(serializers.ModelSerializer):
    article_recipe = BookmarkRecipeSerializer(source='article_recipe_id',read_only=True) # 레시피에 대한 정보 받기
    author_nickname = serializers.CharField(source='article_recipe_id.author.nickname', read_only=True) # 레시피 작성자의 닉네임을 받기

    class Meta:
        model = RecipeBookmark
        # fields = "__all__"
        fields = ['article_recipe','article_recipe_id',"author_nickname","id"]

# 마이페이지에서 작성자의 정보를 확인하기 위한 클래스입니다.


class UserInfoSerializer(serializers.ModelSerializer):

    articles_recipe = ArticleRecipeSerializer(many=True, read_only=True)
    bookmarked_articles = RecipeBookmarkSerializer(
        many=True, read_only=True, source='recipe_bookmark')
    followers = FollowerSerializer(many=True, read_only=True)
    following = FollowingSerializer(many=True, read_only=True)

    """회원 정보 확인"""
    class Meta:
        model = User
        fields = ("email", "user_img", "articles_recipe",
                  "nickname", "following", "bookmarked_articles","followers","is_admin")
        # fields = "__all__"


# 회원 수정을 위한 클래스입니다.
class ProfileUpdateSerializer(serializers.ModelSerializer):

    user_img = serializers.ImageField(required=False)
    email = serializers.EmailField(read_only=True)  
    extra_kwargs = {
        'password': {'write_only': True}
    }

    class Meta:
        model = User
        fields = ['email','nickname', 'password', 'user_img']
        
    # 비밀번호 유효성검사입니다.
    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)

        # Additional password complexity checks
        if (len(value) < 8
            or not (contains_uppercase_letter(value) or contains_lowercase_letter(value))
            or not contains_number(value)
            or not contains_special_character(value)):
            raise serializers.ValidationError("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다.") # 400 non_field_errors

        return value

    def update(self, instance, validated_data):
        """회원 수정을 위한 메서드입니다."""
        password = validated_data.pop("password", None)
        
        # 비밀번호 유효성 검사
        if password:
            password = self.validate_password(password)
        
        
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class UserDataSerializer(serializers.ModelSerializer):
    """ 레시피 정보에서 유저정보 확인용 데이터입니다. """
    class Meta:
        model = User
        fields = ("id", "email", "user_img", "nickname", "following")
        
        
        
# class ProfileUpdateSerializer(serializers.ModelSerializer):
#     nickname = serializers.CharField(required=False)
#     password = serializers.CharField(write_only=True, required=False)
#     user_img = serializers.ImageField(required=False)
#     email = serializers.EmailField(read_only=True)  
#     extra_kwargs = {
#         'password': {'write_only': True}
#     }

#     class Meta:
#         model = User
#         fields = ['email','nickname', 'password', 'user_img']
        
#     # 비밀번호 유효성검사입니다.
#     def validate_password(self, value):
#         try:
#             validate_password(value)
#         except ValidationError as e:
#             raise serializers.ValidationError(e.messages)

#         # Additional password complexity checks
#         if (len(value) < 8
#             or not (contains_uppercase_letter(value) or contains_lowercase_letter(value))
#             or not contains_number(value)
#             or not contains_special_character(value)):
#             raise serializers.ValidationError("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다.") # 400 non_field_errors

#         return value

#     def update(self, instance, validated_data):
#         """회원 수정을 위한 메서드입니다."""
#         password = validated_data.pop("password", None)
#         user_img = validated_data.pop("user_img", None)
#         nickname = validated_data.pop("nickname", None)

#         # 비밀번호 유효성 검사
#         if password is not None:
#             password = self.validate_password(password)

#         if user_img is not None:
#             instance.user_img = user_img

#         if nickname is not None:
#             if User.objects.filter(nickname=nickname).exclude(id=instance.id).exists():
#                 raise serializers.ValidationError({'nickname': '이미 사용중인 닉네임입니다.'})
#             instance.nickname = nickname

#         instance.save()
#         return instance
