import string
from django.core.exceptions import ValidationError

# 특수문자 유효성 검사
def contains_special_character(value):
    for char in value:
        if char in string.punctuation:
            return True
    return False

# 영어 대문자 유효성 검사
def contains_uppercase_letter(value):
    for char in value:
        if char.isupper():
            return True
    return False

# 영어 소문자 유효성 검사
def contains_lowercase_letter(value):
    for char in value:
        if char.islower():
            return True
    return False

# 숫자 유효성 검사
def contains_number(value):
    for char in value:
        if char.isdigit():
            return True
    return False



class CustomPasswordValidator:
    """
    비밀번호가 문자(대문자,소문자 포함), 특수문자, 숫자, 조합 8자리 이상의 비밀번호인지 검증합니다.
    """

    def validate(self, password, user=None):
        if (len(password) < 8
        or not (contains_uppercase_letter(password) or contains_lowercase_letter(password))
        or not contains_number(password)
        or not contains_special_character(password)):
            raise ValidationError(
                ("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다."),
                code="custom_passord",
            )

    def get_help_text(self):
        return ("비밀번호는 8자 이상, 문자, 숫자, 특수문자 조합이어야 합니다.")