from rest_framework import serializers
from users.models import User
from articles.models import ArticleRecipe

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    '''회원가입시 사용자가 보내는 JSON 형태의 데이터를 역직렬화하여 모델 객체 형태의 데이터를 생성하기 위한 Serializer 입니다. '''
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
  
# 마이페이지에서 해당 작성자가 쓴 글을 받기 위한 클래스입니다.
class ArticleRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipe  
        fields = "__all__"

  
  
# 마이페이지에서 작성자의 정보를 확인하기 위한 클래스입니다.
class UserInfoSerializer(serializers.ModelSerializer):
    
    articles_recipe = ArticleRecipeSerializer(many=True, read_only=True)
    
    """회원 정보 확인"""
    class Meta:
        model = User
        fields = ("email", "user_img", "articles_recipe","nickname","following")
        # fields = "__all__"


# 회원 수정을 위한 클래스입니다.
class ProfileUpdateSerializer(serializers.ModelSerializer):
    
    user_img = serializers.ImageField(required=False)
    extra_kwargs = {
        'password': {'write_only': True},
        'email' : {'reade_only': True}
        }
    
    class Meta:
        model = User
        fields = ['email','nickname', 'password', 'user_img'] 
        
    def update(self, instance, validated_data):
        """회원 수정을 위한 메서드입니다."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user















class LoginSerializer(TokenObtainPairSerializer):
    '''로그인시 생성되는 토큰의 payload를 커스텀하기 위한 Serializer입니다.'''

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email
        token['nickname'] = user.nickname
        token['user_img'] = user.user_img.url

        return token