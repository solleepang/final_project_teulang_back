from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
# Create your models here.

class UserManager(BaseUserManager):
    
    ''' 사용자 모델을 생성하고 관리하는 클래스 입니다.'''
    
    def create_user(self, email, password, nickname):
        ''''일반 사용자를 생성합니다.'''
        if not email:
            raise ValueError('유효하지 않은 이메일 형식입니다.')

        user = self.model(
            email=self.normalize_email(email),
            password=password,
            nickname=nickname
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, password, nickname):
        if not email:
            raise ValueError('유효하지 않은 이메일 형식입니다.')

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            nickname=nickname
        )


        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    '''
    커스텀 User 모델 정의

    - email(필수): 로그인 시 사용되는 이메일 주소입니다. + 유니크값
        - 중복 확인이 필요합니다.
    - nickname(필수): 이름 대신 사용되는 닉네임입니다. + 유니크값
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
        - related_name을 followers로 정의해야합니다.
        - symmetrical 는 False로 해야합니다.
    - is_admin : 관리자 권한 여부를 가립니다.    
    - is_active :  계정 활성화 여부를 가립니다.
        - 이메일 인증 기능 구현시 default=False로 변경해야합니다.
    - is_staff : 스태프 권한 여부입니다.
    '''
    
    email = models.CharField('이메일', max_length=255, unique=True)
    nickname = models.CharField('닉네임', max_length=30, unique=True)
    password = models.CharField('비밀번호', max_length=255)
    created_at = models.DateTimeField('회원가입일', auto_now_add=True)
    is_admin = models.BooleanField('관리자 권한 여부', default=False)
    is_active = models.BooleanField('계정 활성화 여부', default=True) # 이메일 인증 완료 시, False로 변경
    is_staff = models.BooleanField('스태브 여부', default=False)
    user_img = models.ImageField('프로필 이미지', upload_to='user/user_img/%Y/%m/%D', default='user_defalt.jpg')
    following = models.ManyToManyField('self', verbose_name='팔로잉', related_name='followers',symmetrical=False, blank=True)
    
    
    object = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname',]
    
    def __str__(self):
        return self.nickname

    def has_perm(self, perm, obj=None):
        return True
    
    def has_module_perms(self, app_label):
        return True

    # @property
    # def is_staff(self):
    #     return self.is_admin
