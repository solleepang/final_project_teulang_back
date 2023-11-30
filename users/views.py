from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from articles.models import ArticleRecipe
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import get_object_or_404
from users.serializers import LoginSerializer, UserSerializer, ProfileUpdateSerializer, UserInfoSerializer, ResetPasswordSerializer
from users.models import User, VerificationCode

from django.core.validators import validate_email
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.contrib.auth.hashers import check_password

# 새로운 사용자를 생성한 후에 이메일 확인 토큰을 생성하고 사용자 모델에 저장합니다. 이메일 인증 링크를 사용자의 이메일 주소로 전송합니다.
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage

import random
from django.utils import timezone
from teulang.settings import env
from teulang import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import get_template


class ResetPasswordView(APIView):


    def post(self, request):
        """
        request body에 있는 이메일이 DB에 저장되어있는지 확인하고,
        랜덤인 숫자 인증 코드를 생성해서 요청 사용자의 이메일에 발송합니다.
        """
        try:
            request_user = User.objects.get(email=request.data['email'])

            # 랜덤으로 6자리 인증 숫자 코드 생성
            randon_num = random.randint(000000,999999)

            # 인증 코드 DB에 저장
            VerificationCode.objects.create(
                user=request_user,
                code=randon_num,
            )

            # 인증 코드의 유효기간 설정
            expiration_period = 3

            # 전송할 이메일의 정보
            subject = "털랭 본인확인을 위한 인증 코드를 확인해주세요."  # 메일 제목
            # 메일 내용
            message = f'인증 코드는 {randon_num}입니다. {expiration_period}분 안에 인증 코드를 입력해 본인 인증을 완료해주세요.'
            from_email = 'teulang@naver.com'
            recipient_list = [request_user.email]

            # 메일 전송
            EmailMessage(subject=subject, body=message,
                            from_email=from_email, to=recipient_list).send()

            return Response({"message": "인증 코드가 담긴 이메일이 전송되었습니다."}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"message":"일치하는 사용자 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)



    def put(self, request):    # request body: {"email":"요청 유저의 이메일", "code": "사용자 입력 인증 코드","new_password":"새로운 비밀번호", "new_password_check":"새로운 비밀번호 확인"}

        """
        이메일과 인증코드를 통해 비밀번호 재설정 권한이 있는지 확인하고,
        새로운 비밀번호, 새로운 비밀번호 확인을 받아서, 검증한 뒤 비밀번호를 재설정합니다.
        """

        # request body에 email, code 값의 유효성 검사
        if not list(request.data.keys()) == ['email', 'code', 'new_password', 'new_password_check']:
            return Response({"message":"request body에 이메일과 코드, 새 비밀번호와 새 비밀번호 확인을 넣어주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            request_user = User.objects.get(email=request.data['email'])
            request_code = request.data['code']
            print(request_user)
            # 사용자에게 보내진 이메일 인증 코드
            verification = VerificationCode.objects.filter(user=request_user.id).order_by('-created_at')
            verification_code = verification[0].code

            # 이메일 인증 유효기간과 인증코드의 생성된 기간
            expiration_period = 13
            generated_period = timezone.now() - verification[0].created_at

            if verification_code != request_code:
                return Response({"message":"코드가 맞지 않습니다. 다시 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            if generated_period.seconds > 60*expiration_period: # 60*13초=13분=유효기간이 지나지 않은 인증 코드 확인
                return Response({"message":"인증코드가 만료되었습니다. 본인인증을 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)

            serializer = ResetPasswordSerializer(request_user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message":"비밀번호가 재설정되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"message":"일치하는 사용자 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class EmailPasswordVerificationView(APIView):


    def post(self, request): # request body: {"code":"숫자 6자리 코드", "email":"요청 이메일"}
        """비밀번호 재설정-이메일을 통한 본인인증을 위해 보낸 인증 코드와 사용자가 입력한 이메일 인증 코드가 일치한지 확인합니다."""

        # request body에 email, code 값의 유효성 검사
        if not list(request.data.keys()) == ['email', 'code']:
            return Response({"message":"request body에 이메일과 코드를 넣어주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 입력한 email로 요청 유저의 데이터와 code값을 정의함
        try:
            request_user = User.objects.get(email=request.data['email'])
            request_code = request.data['code']

            # 사용자에게 보내진 이메일 인증 코드
            verification = VerificationCode.objects.filter(user=request_user.id).order_by('-created_at')
            print(verification)
            verification_code = verification[0].code

            # 이메일 인증 유효기간과 인증코드의 생성된 기간
            expiration_period = 3
            generated_period = timezone.now() - verification[0].created_at

            # DB에 저장된 인증 코드와 유저가 입력한 코드의 일치 여부와 유효기간이 지났는지 확인
            if verification_code == request_code:
                if generated_period.seconds < 60*expiration_period: # 60*3초=3분=유효기간이 지나지 않은 인증 코드 확인
                    return Response({"message":"본인인증 완료됐습니다. 비밀번호 재설정이 가능합니다."}, status=status.HTTP_200_OK)
                return Response({"message":"인증코드가 만료되었습니다. 본인인증을 다시 시도해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"message":"코드가 맞지 않습니다. 다시 입력해주세요."}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            return Response({"message":"일치하는 사용자 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)


class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)

            if default_token_generator.check_token(user, token):
                # 이메일 확인돼서, True로 변경
                user.is_email_verified = True
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
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            # 도메인
            domain_address=env('DOMAIN_ADDRESS')

            # 토큰 생성
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # 이메일에 확인 링크 포함하여 보내기
            verification_url = f"{domain_address}/users/verify-email/{uid}/{token}/"

            # 전송할 이메일의 정보
            subject = "털랭 회원가입 시 등록한 이메일을 인증해주세요."  # 메일 제목
            # 메일 내용
            message = f'다음 링크를 클릭해, 계정을 활성하기 위한 털랭의 회원 이메일 인증을 진행하세요: {verification_url}'
            from_email = 'teulang@naver.com'
            recipient_list = [user.email]

            # html_version = 'email_confirmation_signup.html'
            # html_message = render_to_string(html_version)
            
            # 3
            # template = get_template('email/signup_confirmation.html')
            # html_content = render_to_string(template)

            # send_mail(
            #     subject,
            #     None, # Pass None because it's a HTML mail
            #     from_email,
            #     recipient_list,
            #     fail_silently=False,
            #     html_message = html_content
            # )
            
            #2
            # text_content = "This is an important message."
            html_version = 'email/signup_confirmation.html'
            html_content = render_to_string(html_version,{"verification_url":verification_url})
            # msg = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
            # msg.attach_alternative(html_content, "text/html")
            # msg.send()
            1
            email = EmailMessage(
                subject=subject,
                body=html_content,
                from_email=from_email,
                to=recipient_list
            )
            email.content_subtype = "html"  # Main content is now text/html
            email.send()


            

            # # 메일 전송
            # EmailMessage(subject=subject, body=message,
            #              from_email=from_email, to=recipient_list).send()

            return Response({"message": "회원가입이 완료되었습니다. 인증 이메일이 전송되었습니다."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class DuplicateEmailConfirmView(APIView):
    """이메일 정보를 받아서 고유한 값이면 status 200을, 중복된 값이면 status 409을 반환합니다."""

    def post(self, request):
        email = request.data['email']

        # 이메일 유효성 검사
        try:
            validate_email(email)
            email_list = User.objects.values_list('email', flat=True)

            # 이메일 중복 확인
            if request.data['email'] in email_list:
                return Response({"message": "이미 존재하는 이메일입니다."}, status=status.HTTP_409_CONFLICT)
            return Response({"message": "사용 가능한 이메일입니다."}, status=status.HTTP_200_OK)

        except ValidationError:
            return Response({"message": "이메일 형식이 올바르지 않습니다. 유효한 이메일 주소를 입력하십시오."}, status=status.HTTP_400_BAD_REQUEST)


class DuplicateNicknameConfirmView(APIView):
    """닉네임의 정보를 받아서 고유한 값이면 status 200을, 중복된 값이면 status 409을 반환합니다."""

    def post(self, request):
        nickname_list = User.objects.values_list('nickname', flat=True)
        if request.data['nickname'] in nickname_list:
            return Response({"message": "이미 존재하는 닉네임입니다."}, status=status.HTTP_409_CONFLICT)
        return Response({"message": "사용 가능한 닉네임입니다."}, status=status.HTTP_200_OK)


class LoginView(TokenObtainPairView):
    """
    사용자의 정보를 받아 로그인합니다.
    JWT 토큰 인증 방식을 커스터마이징해서 활용합니다.
    """
    serializer_class = LoginSerializer


# 사용자 정보 확인
class UserDetailView(APIView):
    """
    사용자의 정보를 get요청으로 받아야합니다.
    """

    def get(self, request, user_id, format=None):
        user = get_object_or_404(User, pk=user_id)
        serializer = UserInfoSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# 사용자 정보 수정 및 삭제
class UserUpdateView(APIView):

    """
    로그인한 사람의 정보를 put요청으로 수정해야합니다.
    """
    permission_classes = [IsAuthenticated]
    def put(self, request, user_id, format=None):
        if not request.user.is_authenticated or request.user.id != user_id:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
            
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
        if check_password(password, user.password):  # 회원탈퇴시 비밀번호를 적어야 탈퇴가능!
            user.delete()
            return Response({"message": "회원 탈퇴 완료."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "비밀번호 불일치."}, status=status.HTTP_403_FORBIDDEN)






class FollowView(APIView):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        # 유저의 팔로워들
        follower_serializer = UserSerializer(user.followers, many=True)
        # 유저가 팔로잉하고 있는 사람들
        following_serializer = UserSerializer(user.following, many=True)
        data = {
            'followers': follower_serializer.data,
            'following': following_serializer.data,
        }
        return Response(data)
    
    def post(self, request, user_id):
        if request.user.is_anonymous:
            return Response({'message': '로그인이 필요합니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        me = request.user
        you = User.objects.get(id=user_id)
        if me == you:
            return Response({'message': '본인을 팔로우할 수 없습니다.'},status=status.HTTP_400_BAD_REQUEST)
        
        if you.followers.filter(id=me.id).exists():
            me.following.remove(you)
            me.save()
            return Response({'message': '팔로우 취소합니다.'})
        else:
            me.following.add(you)
            me.save()
            return Response({'message': '팔로우 합니다.'})
    
