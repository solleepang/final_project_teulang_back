from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articles.models import ArticleRecipe
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from users.serializers import LoginSerializer, UserSerializer, ProfileUpdateSerializer, UserInfoSerializer
from users.models import User
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from rest_framework.validators import UniqueValidator


class SignupView(APIView):
    def post(self, request):
        "사용자 정보를 받아 회원가입합니다."
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):   # 오류 메세지 커스텀을 위해서
            user= serializer.save()
            return Response({"message":"회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


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
        if not request.user.is_authenticated or request.user.id != user_id:
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
    def delete(self, request, user_id, format=None):
        user = get_object_or_404(User, pk=user_id)
        if not user.is_authenticated:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        password = request.data.get("password", "")
        if check_password(password, user.password): # 회원탈퇴시 비밀번호를 적어야 탈퇴가능!
            user.delete()
            return Response({"message": "회원 탈퇴 완료."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "비밀번호 불일치."}, status=status.HTTP_403_FORBIDDEN)
        