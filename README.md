# 털랭
<p align="center">
<img src="https://github.com/solleepang/final_project_teulang_back/assets/144214007/eb0be101-81ba-43b5-bcea-3a2c41ddc67e">
</p>


## 프로젝트 정보
내일배움캠프 AI 웹 개발 트랙의 최종 프로젝트입니다.
냉장고에 남는 식재료를 활용한 레시피를 공유하고 추천하는 서비스입니다. 재료를 검색해 재료가 포함된 레시피를 찾을 수 있고, 사용자가 직접 레시피를 등록해 공유할 수 있습니다. 다른 사용자들과 댓글 및 별점, 북마크 기능을 통해 소통할 수 있습니다. 검색 시에, 이미지 인식 AI 프로그램으로 사용자가 직접 사진을 찍을 경우 자동으로 재료를 인식해 레시피가 검색되는 것을 구상했습니다. 또한 사진 촬영 및 레시피 확인을 위해 폰에서도 모두 원활하게 이용할 수 있습니다.
#### 개발 기간: 2023.11.03 ~

## 프로젝트 소개
프로젝트 '털랭'은 '냉털'을 하고 싶은 사람들에게 식재료 기반의 레시피를 제공해주고, 같이 공유할 수 있는 서비스입니다.
자취생들에게 골치거리인 냉장고에 남은 식재료를 검색해 오픈 api 데이터셋의 레시피를 제공합니다.
또한 식재료를 이미지로 촬영해 그 식재료를 인식해 검색을 보다 더 쉽게 할 수 있도록 도와줍니다.
그리고 회원가입과 로그인, 이메일 인증을 거치면, 레시피 작성, 북마크, 댓글 작성 등의 더 많은 기능을 사용할 수 있습니다.


## 팀 소개

- BE,AWS 김민재: 레시피 댓글 CRUD, EC2 배포, 프론트엔드 배포
- FE 김현우: 회원가입, 로그인, 이메일/닉네임 중복확인
- BE 명세인: 회원가입, 로그인, 이메일/닉네임 중복확인, 회원가입 이메일 인증, 비밀번호 재설정
- FE 우은진: 레시피 CRUD, 레시피 댓글 CURD, 레시피 검색, 북마크, 별점, 레시피 함께보기
- BE 이솔: 레시피 검색, 북마크, 별점, 레시피 CRUD, 레시피 함께보기
- AI, BE 이재윤: 레시피 CRUD, 오픈 api 데이터셋 fetch
- AI, BE 조호진: 프로필 수정, 마이페이지, 팔로우, 오픈 api 데이터셋 fetch


## 배포 주소


## 시작 가이드
#### Requirements
- Python 3.10. 이상

#### Installation
```
$ git clone (깃헙 주소)
# cd final_project_teulang_back
```

## 기술 스택
#### Environment
<img src="https://img.shields.io/badge/visual studio code-blue?style=for-the-badge&logo=visualstudiocode&logoColor=white"> <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
#### Development
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
#### Deployment
<img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"> <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"> <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=Gunicorn&logoColor=white">
#### Communication
<img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">

## API 설계
https://teulang.notion.site/2348824ac44846ebadb7feb019630974?v=d885ceee2f274226a19c741dd09ebefc&pvs=4

## 주요 기능
#### 🍽️ 레시피 검색
- 오픈 api로 레시피 데이터 가져와서 풍성한 레시피를 찾아볼 수 있다.
- 식재료를 검색해 관련된 레시피를 찾을 수 있다.
#### 🍽️ 레시피 함께보기
- 북마크한 레시피를 함께 보고 비교할 수 있는 기능이다.
#### 🍽️ 레시피 북마크, 별점 기능으로 레시피 정렬 가능
- 레시피를 북마크하고, 레시피를 별점으로 평가 가능하다.
#### 👥 사용자 팔로우, 회원가입 시 이메일 인증 등

## 서비스 아키텍쳐
<p align="center">
<img src="https://github.com/solleepang/final_project_teulang_back/assets/144214007/114bd6dd-c6c7-4086-90b0-d684e51d1585">
</p>


## 기타 추가 사항 
