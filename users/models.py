from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.


class UserManager(BaseUserManager):
    ''' 사용자 모델을 생성하고 관리하는 클래스 입니다.'''


    def create_user(self, email, password, nickname):
        """'일반 사용자를 생성합니다."""
        if not email:
            raise ValueError("유효하지 않은 이메일 형식입니다.")

        user = self.model(
            email=self.normalize_email(email), password=password, nickname=nickname
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, nickname):
        if not email:
            raise ValueError("유효하지 않은 이메일 형식입니다.")

        user = self.create_user(
            email=self.normalize_email(email), password=password, nickname=nickname
        )

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_email_verified =True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """
    커스텀 User 모델 정의

    - email(필수): 로그인 시 사용되는 이메일 주소입니다.
        - 중복 확인이 필요합니다.
    - nickname(필수): 이름 대신 사용되는 닉네임입니다.
        - 중복 확인이 필요합니다.
    - password : 사용자의 비밀번호입니다.
        - 비밀번호 확인이 필요합니다.
    - created_at : 회원 가입 날짜입니다.
    - point : 글 작성 혹은 커뮤니티 활동시 추가되는 포인트입니다.
        - 부가 기능입니다.
    - user_img : 프로필 상 이미지입니다.
        - 파일 업로드 경로(상대경로)와 디폴트값이 필요합니다.
        - 배포 시엔 업로드 미디어 파일 경로는 절대경로 설정하지 말 것.
    - following : 팔로우 입니다.
        - related_name을 followers로 정의해야 합니다.
        - symmetrical 는 False로 해야 합니다.
    - is_admin : 관리자 권한 여부를 가립니다.
    - is_active :  계정 활성화 여부를 가립니다.
        - 이메일 인증 기능 구현 시 default=False로 변경해야 합니다.
    - is_staff : 스태프 권한 여부입니다.
    - is_email_verified : 이메일 인증 여부에 대해 담고 있습니다.
    """

    email = models.EmailField('이메일', max_length=255, unique=True)
    nickname = models.CharField('닉네임', max_length=30, unique=True)
    password = models.CharField('비밀번호', max_length=255)
    created_at = models.DateTimeField('회원가입일', auto_now_add=True)
    is_admin = models.BooleanField('관리자 권한 여부', default=False)
    is_active = models.BooleanField('계정 활성화 여부', default=True)
    is_staff = models.BooleanField('스태브 여부', default=False)
    user_img = models.ImageField('프로필 이미지', upload_to='user/user_img/%Y/%m/%D', default='user_defalt.jpg')
    following = models.ManyToManyField('self', verbose_name='팔로잉', related_name='followers',symmetrical=False, blank=True)
    is_email_verified = models.BooleanField('이메일 검증 여부', default=False)

    point = models.IntegerField(default=0)
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname',]





    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


class VerificationCode(models.Model):
    """
    비밀번호 재설정을 위한 이메일에 담긴 숫자 인증 코드 저장을 위한 모델

    - created_at : 인증을 위한 숫자 코드의 생성시간입니다.
        - 이 숫자 코드의 유효 기간을 구현하기 위한 필드입니다.
    - user : 특정 사용자의 인증 코드인지 판단하기 위한 필드입니다.
    - code : 사용자가 비밀번호 재설정을 원해서 이메일 인증 코드 발송을 택하면, 생성돼 DB에 저장됩니다.
    """

    created_at = models.DateTimeField('인증 코드 생성시간', auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, verbose_name="이메일 전송된 인증 코드", related_name="codes")
    code = models.CharField('숫자 인증 코드', max_length=6)