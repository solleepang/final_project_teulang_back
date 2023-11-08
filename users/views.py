from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from users.serializers import LoginSerializer, UserSerializer, ProfileUpdateSerializer, UserInfoSerializer
from users.models import User

from rest_framework.permissions import IsAuthenticated

from django.core.validators  import validate_email
from django.core.exceptions  import ValidationError


class SignupView(APIView):
    def post(self, request):
        "사용자 정보를 받아 회원가입합니다."
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):   # 오류 메세지 커스텀을 위해서
            user= serializer.save()
            return Response({"message":"회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DuplicateEmailConfirmkView(APIView):
    """이메일 정보를 받아서 고유한 값이면 status 200을, 중복된 값이면 status 409을 반환합니다."""
    def post(self, request):
        email = request.data['email']

        # 이메일 유효성 검사
        try:
            validate_email(email)
            email_list=User.objects.values_list('email', flat=True)

            # 이메일 중복 확인
            if request.data['email'] in email_list:
                return Response({"message":"이미 존재하는 이메일입니다."}, status=status.HTTP_409_CONFLICT)
            return Response({"message":"사용 가능한 이메일입니다."}, status=status.HTTP_200_OK)

        except ValidationError:
            return Response({"message" : "이메일 형식이 올바르지 않습니다. 유효한 이메일 주소를 입력하십시오."}, status=status.HTTP_400_BAD_REQUEST)



class DuplicateNicknameConfirmView(APIView):
    """닉네임의 정보를 받아서 고유한 값이면 status 200을, 중복된 값이면 status 409을 반환합니다."""
    def post(self, request):
        nickname_list=User.objects.values_list('nickname', flat=True)
        if request.data['nickname'] in nickname_list:
            return Response({"message":"이미 존재하는 닉네임입니다."}, status=status.HTTP_409_CONFLICT)
        return Response({"message":"사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    """
    사용자의 정보를 받아 로그인합니다.
    JWT 토큰 인증 방식을 커스터마이징해서 활용합니다.
    """
    serializer_class = LoginSerializer
    
    
    
# 사용자 정보 및 회원정보 수정
class UserDetailView(APIView):
    """
    사용자의 정보를 get요청으로 받아야합니다.
    """
    def get(self, request, user_id, format=None):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    """
    로그인한 사람의 정보를 put요청으로 수정해야합니다.
    """
    def put(self, request,user_id,format=None):
        if not request.user.is_authenticated:
            Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    """
    사용자의 정보를 delete요청으로 회원탈퇴를 진행합니다.
    """
    