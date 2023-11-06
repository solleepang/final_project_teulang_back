from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView

from users.serializers import UserSerializer


class SignupView(APIView):
    def post(self, request):
        "사용자 정보를 받아 회원가입합니다."
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user= serializer.save()
            return Response({"message":"회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)