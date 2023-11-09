from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articles.models import ArticleRecipe
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from users.serializers import LoginSerializer, UserSerializer, ProfileUpdateSerializer, UserInfoSerializer
from users.models import User

from django.core.validators  import validate_email
from django.core.exceptions  import ValidationError

from django.contrib.auth.hashers import check_password

# 새로운 사용자를 생성한 후에 이메일 확인 토큰을 생성하고 사용자 모델에 저장합니다. 이메일 인증 링크를 사용자의 이메일 주소로 전송합니다.
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage


class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)

            if default_token_generator.check_token(user, token):
                user.is_active = True # 이메일 확인 여부 필드(is_email_verified)를 정의하면, 그것으로 대체 예정
                user.save()
                return Response({"message": "이메일 확인이 완료되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "이메일 확인 링크가 잘못되었습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": "사용자를 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)




class SignupView(APIView):
    def post(self, request):
        """사용자 정보를 받아 회원가입합니다."""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):   # 오류 메세지 커스텀을 위해서
            user= serializer.save()

            # 토큰 생성
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # 이메일에 확인 링크 포함하여 보내기
            verification_url = f"http://127.0.0.1:8000/users/verify-email/{uid}/{token}/"

            # 전송할 이메일의 정보
            subject = "털랭 회원가입 시 등록한 이메일을 인증해주세요." # 메일 제목
            message = f'다음 링크를 클릭해, 계정을 활성하기 위한 털래의 회원 이메일 인증을 진행하세요: {verification_url}' # 메일 내용
            from_email = 'teulang@naver.com'
            recipient_list = [user.email]

            # 메일 전송
            EmailMessage(subject=subject, body=message,from_email=from_email, to=recipient_list).send()

            return Response({"message":"회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class DuplicateEmailConfirmView(APIView):
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
