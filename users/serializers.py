from rest_framework import serializers
from users.models import User


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