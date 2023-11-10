import string

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


