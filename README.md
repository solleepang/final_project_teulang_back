# 털랭
<p align="center">
<img src="https://github.com/solleepang/final_project_teulang_back/assets/144214007/eb0be101-81ba-43b5-bcea-3a2c41ddc67e">
</p>


## 프로젝트 정보
내일배움캠프 AI 웹 개발 트랙의 최종 프로젝트입니다.
냉장고에 남는 식재료를 활용한 레시피를 공유하고 추천하는 서비스입니다. 재료를 검색해 재료가 포함된 레시피를 찾을 수 있고, 사용자가 직접 레시피를 등록해 공유할 수 있습니다. 다른 사용자들과 댓글 및 별점, 북마크 기능을 통해 소통할 수 있습니다. 검색 시에, 이미지 인식 AI 프로그램으로 사용자가 직접 사진을 찍을 경우 자동으로 재료를 인식해 레시피가 검색되는 것을 구상했습니다. 또한 사진 촬영 및 레시피 확인을 위해 폰에서도 모두 원활하게 이용할 수 있습니다.
#### 개발 기간: 2023.11.03 ~ 2023.12.07

## 프로젝트 소개

프로젝트 '털랭'은 '냉털'을 하고 싶은 사람들에게 식재료 기반의 레시피를 제공해주고, 같이 공유할 수 있는 서비스입니다.
요리명을 통해 특정 레시피를 찾는 기존의 서비스와 달리 재료명을 검색하여 여러 레시피를 확인하는 것이 저희 프로젝트의 주요 컨셉입니다.
자취생들에게 골치거리인 냉장고에 남은 식재료를 검색해, 오픈 api 데이터셋의 레시피를 제공합니다.
또한 식재료를 이미지로 촬영해 그 식재료를 인식해 검색을 보다 더 쉽게 할 수 있도록 도와줍니다.
키워드와 이미지로 식재료를 검색하여 레시피를 찾을 수 있고 사용자가 직접 레시피를 등록하는 것도 가능합니다.
외에도 회원가입과 로그인, 이메일 인증을 거치면, 레시피 작성, 북마크, 댓글 작성 등의 더 많은 기능을 사용할 수 있습니다.
털랭 서비스는 이미지 검색 및 요리 시에 레시피 확인이 용이하도록, 스마트폰 환경도 지원하여 서비스의 기획의도를 더욱 살렸습니다.


## 팀 소개

- BE,AWS 김민재: 레시피 댓글 CRUD, EC2 배포, 프론트엔드 배포
- FE 김현우: 회원가입, 로그인, 이메일/닉네임 중복확인, 비밀번호 재설정, 소셜로그인, 프로필 수정, 마이페이지, 내 냉장고, 팔로우, 네비게이션, 디자인
- BE 명세인: 회원가입, 로그인, 이메일/닉네임 중복확인, 회원가입 이메일 인증, 비밀번호 재설정
- FE 우은진: 레시피 CRUD, 레시피 댓글 CURD, 레시피 검색, 북마크, 별점, 레시피 함께보기, 자유게시판 CRUD, 메인페이지, 디자인
- BE 이솔: 레시피 검색, 북마크, 별점, 레시피 CRUD, 레시피 함께보기, 내 냉장고, 자유게시판 게시글/댓글 CRUD
- AI, BE 이재윤: 레시피 CRUD, 오픈 api 데이터셋 fetch, 이미지 검색, 레시피 간단설명 요약
- AI, BE 조호진: 프로필 수정, 마이페이지, 팔로우, 오픈 api 데이터셋 fetch, 이미지 검색, 유튜브 영상 요약


## 배포 주소
<a href="https://teulang.net/">털랭 사이트 바로가기</a>

## 시작 가이드
#### Requirements
- Python 3.10. 이상

#### Installation
```
$ git clone (깃헙 주소)
$ cd final_project_teulang_back
```
#### mac user - local
```
$ brew install ffmpeg
```

## 기술 스택
#### Environment
<img src="https://img.shields.io/badge/visual studio code-blue?style=for-the-badge&logo=visualstudiocode&logoColor=white"> <img src="https://img.shields.io/badge/git-F05032?style=for-the-badge&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/github-181717?style=for-the-badge&logo=github&logoColor=white">
#### Development
<img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
#### Deployment
<img src="https://img.shields.io/badge/linux-FCC624?style=for-the-badge&logo=linux&logoColor=black"> <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> <img src="https://img.shields.io/badge/nginx-009639?style=for-the-badge&logo=nginx&logoColor=white"> <img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=Gunicorn&logoColor=white"> <img src="https://img.shields.io/badge/amazonrds-#527FFF?style=for-the-badge&logo=AmazonRDSColor=white"> <img src="https://img.shields.io/badge/amazonroute53-##8C4FFF?style=for-the-badge&logo=AmazonRoute53Color=white">
#### Communication
<img src="https://img.shields.io/badge/slack-4A154B?style=for-the-badge&logo=slack&logoColor=white">

## API 설계
https://teulang.notion.site/2348824ac44846ebadb7feb019630974?v=d885ceee2f274226a19c741dd09ebefc&pvs=4

## 주요 기능
#### 🍽️ 레시피 검색
- 오픈 api로 레시피 데이터 가져와서 풍성한 레시피를 찾아볼 수 있습니다.
- 식재료를 키워드와 이미지를 통해 검색하여 관련된 레시피를 찾을 수 있습니다.
#### 🍽️ 레시피 함께보기
- 북마크한 레시피를 함께 보고 비교할 수 있는 기능입다.
#### 🍽️ 레시피 북마크, 별점 기능으로 레시피 정렬 가능
- 레시피를 북마크하고, 레시피를 별점으로 평가 가능합니다.
#### 🍽️ 내 냉장고 기능
- 집 냉장고의 식재료들을 관리하고 소비기한이 얼마 남지 않은 식재료를 이용한 레시피를 추천받을 수 있습니다.
#### 👥 회원 기능
- 회원가입, 로그인, 로그아웃이 가능합니다.
- 사용자들간의 팔로우가 가능합니다.
- 회원가입 시 이메일 인증이 이뤄져야 레시피/게시판의 글을 작성할 수 있습니다.
- 비밀번호를 잊은 사용자들이 비밀번호를 재설정할 수 있습니다.
- 카카오 소셜 로그인이 가능합니다.

## 서비스 아키텍쳐
<p align="center">
<img src="https://github.com/solleepang/final_project_teulang_back/assets/144214007/55b68ec2-1d11-4e64-a80f-cbf43039e9af" alt="서비스아키텍쳐 이미지" >
</p>

## 기타 사항
- 백엔드 배포 자동화가 이뤄져 있지 않음
- 데이터베이스가 SQLite로 사용됨.
