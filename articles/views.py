import requests
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
    RecipeBookmark,
    ArticlesFree,
    ArticleFreeImages,
    CommentArticlesFree,
)
from articles.serializers import (
    RecipeSerializer,
    RecipeCreateSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    IngredientSerializer,
    IngredientCreateSerializer,
    StarRateSerializer,
    RecipeBookmarkSerializer,
    RecipeCommentSerializer,
    FreeCommentSerializer,
    FreeImagesSerializer,
    FreeArticleSerializer,
)
from users.models import User
from django.core.exceptions import ObjectDoesNotExist
from teulang.settings import env
from django.core.paginator import Paginator
from django.db.models import Count

from ultralytics import YOLO
import cv2 as cv
import tempfile
import os
from django.conf import settings
from datetime import datetime
import re
from pytube import YouTube
from moviepy.editor import *
import openai
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

class RecipeView(APIView):
    # 레시피 불러오기(전체, 정렬(인기순/최신순))
    def get(self, request):
        """전체,인기순,최신순 parameter 값에 따라 20개의 게시물 반환
        param page = int (None 이면 1)
        param option = latest(최신순) or bookmark(인기순)"""

        page = request.GET.get("page", 1) if request.GET.get("page", 1) else 1
        option = request.GET.get("option")
        # 옵션 없을 경우 id 순
        recipes = ArticleRecipe.objects.all()
        if option == "latest":  # 최신순
            recipes = recipes.order_by("-created_at")
        elif option == "bookmark":  # 인기순(북마크 많은 순)
            recipes = recipes.annotate(
                bookmark_count=Count("recipe_bookmark")
            ).order_by("-bookmark_count")
        all_recipes_paginator = Paginator(recipes, 20)
        page_obj = all_recipes_paginator.page(page)
        paginator_data = {
            "filtered_recipes_count": all_recipes_paginator.count,  # 검색된 레시피 개수
            "pages_num": all_recipes_paginator.num_pages,  # 총 페이지 수
        }
        serializer = RecipeSerializer(page_obj, many=True)
        return Response({"pagenation_data": paginator_data, "serializer_data": serializer.data}, status=status.HTTP_200_OK)

    # 레시피, 재료, 순서 생성
    def post(self, request):
        """레시피 생성 - 재료/순서 함께 생성"""
        # 레시피 작성 권한 설정(로그인, 이메일 인증)
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if request.user.is_email_verified == False:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )
        # 레시피 저장
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save(author=request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 재료 저장
        ingredients = request.data.get("recipe_ingredients")
        if ingredients:
            ingredients = ingredients.split(",")
            for ingredient in ingredients:
                ingredient_data = {"ingredients": ingredient}
                serializer_ingredients = IngredientCreateSerializer(
                    data=ingredient_data
                )
                if serializer_ingredients.is_valid():
                    serializer_ingredients.save(article_recipe_id=recipe.id)
                else:
                    return Response(
                        serializer_ingredients.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        else:
            pass
        # 조리 순서와 이미지 저장
        orders = request.data.get("recipe_order")
        if orders:
            orders = eval(orders)
            for i in range(1, len(orders) + 1):
                recipe_img = request.data.get(f"{i}")
                order_image_data = {
                    "order": i,
                    "content": orders[i - 1]["content"],
                    "recipe_img": recipe_img if recipe_img else None,
                }
                order_image_serializer = OrderCreateSerializer(data=order_image_data)
                if order_image_serializer.is_valid():
                    order_image_serializer.save(article_recipe_id=recipe.id)
                else:
                    return Response(
                        order_image_serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST,
                    )
        else:
            pass
        final_serializer = RecipeSerializer(recipe)
        return Response(final_serializer.data, status=status.HTTP_200_OK)


class RecipeDetailView(APIView):
    # 상세 레시피 불러오기
    def get(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        serializer = RecipeSerializer(recipe)
        if request.user.is_anonymous:
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            rate = StarRate.objects.filter(
                article_recipe_id=article_recipe_id, user_id=request.user.id
            )
            user_data = {
                "request_user_article_data": {
                    "request_user": request.user.nickname,
                    "is_bookmarked": True
                    if RecipeBookmark.objects.filter(
                        article_recipe_id=article_recipe_id, user_id=request.user.id
                    )
                    else False,
                    "is_star_rated": True if rate else False,
                    "star_rate": rate[0].star_rate if rate else None,
                }
            }
            user_data.update(serializer.data)
            return Response(user_data, status=status.HTTP_200_OK)

    # 레시피 수정하기
    def put(self, request, article_recipe_id):
        """레시피 수정 - 재료/순서 수정,삭제,생성"""
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:
            serializer = RecipeCreateSerializer(recipe, data=request.data)
            # 레시피 수정
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # 재료 수정
            ingredients_data = request.data.get("recipe_ingredients")
            if ingredients_data:
                ingredients_data = eval(ingredients_data)
                for ingredient_data in ingredients_data:
                    try:
                        ingredient = ArticleRecipeIngredients.objects.get(
                            id=ingredient_data["id"], article_recipe=recipe
                        )
                    except ObjectDoesNotExist:
                        # 재료 생성
                        ingredients_serializer = IngredientCreateSerializer(
                            data=ingredient_data
                        )
                        if ingredients_serializer.is_valid():
                            ingredients_serializer.save(article_recipe_id=recipe.id)
                        else:
                            return Response(
                                ingredients_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    else:
                        # 재료 수정
                        ingredients_serializer = IngredientCreateSerializer(
                            ingredient, data=ingredient_data
                        )
                        if ingredients_serializer.is_valid():
                            ingredients_serializer.save()
                        else:
                            return Response(
                                ingredients_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )
            else:
                pass
            # 순서 수정
            orders_data = request.data.get("recipe_order")
            if orders_data:
                orders_data = eval(orders_data)
                for order_data in orders_data:
                    recipe_order_img = request.data.get(f'{order_data["order"]}')
                    order_data["recipe_img"] = (
                        recipe_order_img if recipe_order_img else None
                    )
                    try:
                        order = RecipeOrder.objects.get(
                            id=order_data["id"], article_recipe=recipe
                        )
                    except ObjectDoesNotExist:
                        # 순서 생성
                        order_serializer = OrderCreateSerializer(data=order_data)
                        if order_serializer.is_valid():
                            order_serializer.save(article_recipe_id=recipe.id)
                        else:
                            return Response(
                                order_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )
                    else:
                        # 순서 수정
                        order_serializer = OrderCreateSerializer(order, data=order_data)
                        if order_serializer.is_valid():
                            order_serializer.save()
                        else:
                            return Response(
                                order_serializer.errors,
                                status=status.HTTP_400_BAD_REQUEST,
                            )
            else:
                pass
            # 재료 삭제
            delete_ingredients_data = request.data.get("delete_ingredients")
            if delete_ingredients_data:
                delete_ingredients_data = eval(delete_ingredients_data)
                for delete_ingredient in delete_ingredients_data:
                    ingredient = get_object_or_404(
                        ArticleRecipeIngredients,
                        id=delete_ingredient,
                        article_recipe_id=recipe.id,
                    )
                    ingredient.delete()
            else:
                pass
            # 순서 삭제
            delete_order_data = request.data.get("delete_order")
            if delete_order_data:
                delete_order_data = eval(delete_order_data)
                for delete_order in delete_order_data:
                    order = get_object_or_404(
                        RecipeOrder, id=delete_order, article_recipe_id=recipe.id
                    )
                    order.delete()
            else:
                pass
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)
        final_serializer = RecipeSerializer(recipe)
        return Response(final_serializer.data, status=status.HTTP_200_OK)

    # 레시피 삭제하기
    def delete(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:
            recipe.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


# class OrderView(APIView):
#     # 각 레시피의 조리 순서 전부 가져오기
#     def get(self, request, article_recipe_id):
#         recipe = ArticleRecipe.objects.get(id=article_recipe_id)
#         recipe_orders = recipe.recipe_order.all()  # order_set -> recipe_order
#         serializer = OrderSerializer(recipe_orders, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class OrderDetailView(APIView):
#     # 각 레시피의 조리순서 수정하기 (하나씩 각각)
#     def put(self, request, article_recipe_id, recipe_order_id):
#         recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
#         # recipe_order = get_object_or_404(RecipeOrder, id=recipe_order_id) ==> 식재료와 마찬가지로 오류 수정
#         recipe_order = recipe.recipe_order.get(id=recipe_order_id)
#         if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 수정 안되게 설정
#             serializer = OrderCreateSerializer(recipe_order, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

#     # 각 레시피의 조리순서 삭제하기 (하나씩 각각)
#     def delete(self, request, article_recipe_id, recipe_order_id):
#         recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
#         recipe_order = recipe.recipe_order.get(id=recipe_order_id)
#         if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
#             recipe_order.delete()
#             return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


# class IngredientView(APIView):
#     # 각 레시피의 재료 전부 가져오기
#     def get(self, request, article_recipe_id):
#         recipe = ArticleRecipe.objects.get(id=article_recipe_id)
#         recipe_ingredients = recipe.recipe_ingredients.all()
#         serializer = IngredientSerializer(recipe_ingredients, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class IngredientDetailView(APIView):
#     # 각 레시피의 재료 수정하기 (하나씩 각각)
#     def put(self, request, article_recipe_id, article_recipe_ingredients_id):
#         recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
#         # url에서 받아온 recipe_id값과 동일한 recipe 내에서 역참조한 식재료 목록 중 ingredients_id와 같은 값을 갖는 식재료 목록을 하나씩 가져옵니다.
#         recipe_ingredients = recipe.recipe_ingredients.get(
#             id=article_recipe_ingredients_id
#         )
#         if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 수정 안되게 설정
#             serializer = IngredientCreateSerializer(
#                 recipe_ingredients, data=request.data
#             )
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_200_OK)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

#     # 각 레시피의 재료 삭제하기 (하나씩 각각)
#     def delete(self, request, article_recipe_id, article_recipe_ingredients_id):
#         recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
#         recipe_ingredients = recipe.recipe_ingredients.get(
#             id=article_recipe_ingredients_id
#         )
#         if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
#             recipe_ingredients.delete()
#             return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
#         else:
#             return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class StarRateView(APIView):
    def post(self, request, article_recipe_id):
        """요청 유저 아이디로 해당 레시피에 별점 추가"""
        if not request.user.is_email_verified:
            return Response({"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN)
        # 로그인 정보 확인
        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist:
            return Response("로그인 정보가 없습니다.", status=status.HTTP_401_UNAUTHORIZED)
        # 요청한 레시피 있는지 확인
        try:
            recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        except ObjectDoesNotExist:
            return Response("존재하지 않는 레시피입니다.", status=status.HTTP_400_BAD_REQUEST)
        # 본인의 글인지 확인
        if recipe.author == request.user:
            return Response("자신의 글에는 별점을 매길 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

        try:
            StarRate.objects.get(user_id=user, article_recipe_id=article_recipe_id)
        except ObjectDoesNotExist:
            # 별점이 존재하지 않으면 새로 추가
            serializer = StarRateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user_id=user, article_recipe_id=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)
        else:
            # 별점 중복 확인
            return Response("이미 작성한 별점이 있습니다.", status=status.HTTP_409_CONFLICT)

    def delete(self, request, article_recipe_id):
        recipe_star_rate = get_object_or_404(
            StarRate, id=article_recipe_id, user_id=request.user.id
        )
        recipe_star_rate.delete()
        return Response("별점이 삭제되었습니다", status=status.HTTP_204_NO_CONTENT)


class RecipeUserBookmarkView(APIView):
    def get(self, request):
        """요청 유저의 북마크 반환"""
        if request.user.is_anonymous:
            return Response("로그인 해주세요.", status=status.HTTP_401_UNAUTHORIZED)
        else:
            bookmark = ArticleRecipe.objects.filter(
                recipe_bookmark__user_id=request.user.id
            )
            serializer = RecipeSerializer(bookmark, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class RecipeBookmarkView(APIView):
    def post(self, request, article_recipe_id):
        """요청 유저 아이디로 해당 레시피를 북마크 추가"""
        # 로그인 정보 확인
        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist:
            return Response("로그인 정보가 없습니다.", status=status.HTTP_401_UNAUTHORIZED)
        # 요청한 레시피 있는지 확인
        try:
            recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        except ObjectDoesNotExist:
            return Response("존재하지 않는 레시피입니다.", status=status.HTTP_400_BAD_REQUEST)

        try:
            bookmark = RecipeBookmark.objects.get(
                user_id=user, article_recipe_id=article_recipe_id
            )
        except ObjectDoesNotExist:
            # 북마크 정보가 존재하지 않으면 새로 추가
            serializer = RecipeBookmarkSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user_id=user, article_recipe_id=recipe)
                return Response("북마크가 저장되었습니다.", status=status.HTTP_201_CREATED)
            else:
                return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)
        else:
            # 북마크 정보가 존재하면 북마크 삭제
            bookmark.delete()
            return Response("북마크가 취소되었습니다.", status=status.HTTP_200_OK)


class CommentView(APIView):
    def get(self, request, article_recipe_id):
        """특정 recipe의 댓글 조회"""
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comments = recipe.article_recipe_comment.all()
        serializer = RecipeCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_recipe_id):
        """댓글 작성"""
        # 권한 설정
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if request.user.is_email_verified == False:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )
        serializer = RecipeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, article_recipe_id=article_recipe_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_recipe_id, recipe_comment_id):
        """댓글 수정"""
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comment = recipe.article_recipe_comment.get(id=recipe_comment_id)
        serializer = RecipeCommentSerializer(comment, data=request.data)
        if request.user == comment.author:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (
            request.user.is_authenticated == False
        ):  # request.user.is_anonymous == True를 지금과 같은 형태로 변경
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)
        elif request.user != comment.author:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_recipe_id, recipe_comment_id):
        """댓글 삭제"""
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comment = recipe.article_recipe_comment.get(id=recipe_comment_id)
        if request.user == comment.author:
            comment.delete()
            return Response("댓글이 삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        elif request.user.is_authenticated == False:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class RecipeSearchView(APIView):
    def get(self, request):
        """검색된 재료 포함하는 레시피 구한 후 전체,인기순,최신순 parameter 값에 따라 20개의 게시물 반환
        param page = int (None 이면 1)
        param option = latest(최신순) or bookmark(인기순)"""

        # 검색 재료 포함하는 레시피 포함
        quart_string = request.GET.get("q", "")
        ingredients = quart_string.split(",")
        recipes = []
        for i in range(len(ingredients)):
            if i < 1:
                recipes = ArticleRecipe.objects.filter(
                    recipe_ingredients__ingredients__contains=ingredients[i].strip()
                ).distinct()
            else:
                recipes = recipes.filter(
                    recipe_ingredients__ingredients__contains=ingredients[i].strip()
                ).distinct()
        # 최신순/인기순 옵션과 페이지네이션
        page = request.GET.get("page", 1) if request.GET.get("page", 1) else 1
        option = request.GET.get("option")

        # 옵션 없을 경우 id 순
        if option == "latest":  # 최신순
            recipes = recipes.order_by("-created_at")
        elif option == "bookmark":  # 인기순(북마크 많은 순)
            recipes = recipes.annotate(
                bookmark_count=Count("recipe_bookmark")
            ).order_by("-bookmark_count")

        recipes_paginator = Paginator(recipes, 20)
        if int(page) > recipes_paginator.num_pages:
            # 존재하는 것보다 많은 페이지 요청시 메시지 반환
            return Response("해당 페이지가 없습니다.", status=status.HTTP_404_NOT_FOUND)
        page_obj = recipes_paginator.page(page)
        paginator_data = {
            "filtered_recipes_count": recipes_paginator.count,  # 검색된 레시피 개수
            "pages_num": recipes_paginator.num_pages,  # 총 페이지 수
        }
        serializer = RecipeSerializer(page_obj, many=True)

        return Response(
            {"pagenation_data": paginator_data, "serializer_data": serializer.data},
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])  # 데코레이터 추가
@permission_classes([IsAuthenticated])  # 권한 설정 데코레이터 추가
def fetch_and_save_openapi_data(request, start, end):
    if not request.user.is_admin:  # 권한 설정 추가
        return Response(
            "권한이 없습니다.", status=status.HTTP_403_FORBIDDEN
        )  # 권한 설정 추가 (관리자로 로그인한 access token값으로 확인합니다.)

    # api키 받기
    api_key = env("API_KEY")

    # API URL 입력 (맨뒤 1124 입력후 urls.py의 경로로 get 요청시 레시피를 가져옵니다.)
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/{start}/{end}"
    response = requests.get(url)

    if response.status_code == 200:
        response_data = response.json()

        # JSON 응답 데이터에서 레시피 목록을 가져옴
        recipes = response_data["COOKRCP01"]["row"]

        # 각 레시피에 대한 데이터를 순회하면서 저장
        for recipe_data in recipes:
            article_recipe = ArticleRecipe.objects.create(
                author_id=1,  # 작성자 ID는 일단 1번으로 했습니다.
                title=recipe_data["RCP_NM"],
                api_recipe=True,
                recipe_thumbnail_api=recipe_data["ATT_FILE_NO_MK"],
            )

            # 재료 저장
            ingredients = recipe_data["RCP_PARTS_DTLS"].split(",")
            for ingredient in ingredients:
                ArticleRecipeIngredients.objects.create(
                    article_recipe=article_recipe, ingredients=ingredient.strip()
                )

            # 레시피 순서 저장
            for i in range(1, 21):  # 1에서 20까지의 순서로 데이터가 있음
                order_key = f"MANUAL{i:02d}"
                img_key = f"MANUAL_IMG{i:02d}"
                content = recipe_data.get(order_key, "")[3:]
                img_url = recipe_data.get(img_key, "")
                if content:
                    RecipeOrder.objects.create(
                        article_recipe=article_recipe,
                        content=content,
                        recipe_img_api=img_url,
                        order=i,
                    )

        return JsonResponse({"message": "데이터 가져오기 및 저장 완료"})
    else:
        return JsonResponse({"error": "데이터 가져오기 실패"}, status=500)


# class DetectObjectsAPI(APIView):
#     def post(self, request, *args, **kwargs):
#         # YOLO 모델 불러오기
#         model = YOLO("best.pt")

#         # POST 요청으로부터 이미지 파일 얻기
#         image = request.FILES.get("image")

#         # 입력 이미지를 임시 파일로 저장
#         input_image_path = os.path.join(settings.MEDIA_ROOT, "temp_input_image.jpg")
#         with open(input_image_path, "wb") as destination:
#             for chunk in image.chunks():
#                 destination.write(chunk)

#         # YOLO 모델을 사용하여 객체 감지 수행
#         results = model.predict(source=input_image_path, device="cpu")[0]

#         # 클래스 이름 얻기
#         class_names = results.names

#         # 중복 제거된 감지된 클래스 얻기
#         detected_classes_set = set([class_names[int(r)] for r in results.boxes.cls])
#         detected_classes = list(detected_classes_set)

#         # 출력 이미지를 저장할 디렉토리 생성
#         output_directory = os.path.join(settings.MEDIA_ROOT, "detected_images")
#         os.makedirs(output_directory, exist_ok=True)

#         # 출력 이미지의 랜덤 파일명 생성
#         output_image_path = os.path.join(
#             output_directory, f"output_{hash(input_image_path)}.png"
#         )

#         # 경계 상자와 주석이 추가된 이미지를 그려서 저장
#         result_plotted = results.plot(line_width=1)
#         cv.imwrite(output_image_path, result_plotted)

#         # 임시 입력 이미지 파일 삭제
#         os.remove(input_image_path)

#         # Response 데이터 구성
#         response_data = {
#             "detected_classes": detected_classes,
#             "output_image_path": output_image_path,
#         }

#         return Response(response_data)


class DetectObjectsAPI(APIView):
    def post(self, request):
        # YOLO 모델 불러오기
        model = YOLO("best.pt")

        # POST 요청으로부터 이미지 파일 얻기
        image = request.FILES.get("image")

        # 이미지를 임시 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            temp_image.write(image.read())
            temp_image_path = temp_image.name

        # YOLO 모델을 사용하여 객체 감지 수행
        results = model.predict(source=temp_image_path, device="cpu")[0]

        # 클래스 이름 얻기
        class_names = results.names

        # 중복 제거된 감지된 클래스 얻기
        detected_classes_set = set([class_names[int(r)] for r in results.boxes.cls])
        detected_classes = list(detected_classes_set)

        # 출력 이미지를 저장할 디렉토리 생성
        output_directory = os.path.join(settings.MEDIA_ROOT, "detected_images")
        os.makedirs(output_directory, exist_ok=True)

        # 현재 시간을 이용하여 파일명 생성
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        output_image_path = os.path.join(output_directory, f"output_{current_time}.png")

        # 경계 상자와 주석이 추가된 이미지를 그려서 저장
        result_plotted = results.plot(line_width=1)
        cv.imwrite(output_image_path, result_plotted)

        # 임시 이미지 파일 삭제
        os.remove(temp_image_path)

        # Response 데이터 구성
        response_data = {
            "detected_classes": detected_classes,
            "output_image_path": output_image_path,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class ArticleFreeView(APIView):
    def get(self, request):
        """자유게시판 전체 게시글+이미지+댓글 조회"""
        page = request.GET.get("page", 1) if request.GET.get("page", 1) else 1
        free_article = ArticlesFree.objects.all()
        all_free_paginator = Paginator(free_article, 20)
        paginator_data = {
            "filtered_recipes_count": all_free_paginator.count,  # 검색된 레시피 개수
            "pages_num": all_free_paginator.num_pages,  # 총 페이지 수
        }
        if int(page) > all_free_paginator.num_pages:
            return Response("요청한 페이지가 없습니다.", status=status.HTTP_404_NOT_FOUND)
        page_obj = all_free_paginator.page(page)
        serializer = FreeArticleSerializer(page_obj, many=True)
        return Response(
            {"pagenation_data": paginator_data, "serializer_data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """자유게시판 게시글 작성"""
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_email_verified:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = FreeArticleSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(author_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleFreeDetailView(APIView):
    def get(self, request, article_free_id):
        """자유게시판 특정 게시글+이미지+댓글 조회"""
        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        serializer = FreeArticleSerializer(free_article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, article_free_id):
        """자유게시판 특정 게시글+이미지 수정"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        if request.user == free_article.author_id:
            # 게시글 수정
            free_article_serializer = FreeArticleSerializer(
                free_article, data=request.data
            )
            if free_article_serializer.is_valid():
                free_article_serializer.save()
            else:
                return Response(
                    free_article_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            # 이미지 추가
            new_images = request.FILES
            if new_images:
                for image in new_images.getlist("image"):
                    ArticleFreeImages.objects.create(
                        article_free_id=free_article, free_image=image
                    )
            # 이미지 삭제
            delete_images = request.data.get("delete_image")
            error_text = []
            if delete_images:
                print(type(delete_images))
                delete_images = eval(delete_images)
                for delete_image in delete_images:
                    try:
                        delete_image_id = ArticleFreeImages.objects.get(
                            id=delete_image, article_free_id=free_article
                        )
                    except ObjectDoesNotExist:
                        error_text.append(
                            f"delete_image_error: db에서 [id:{delete_image}] 이미지 정보를 찾지 못했습니다."
                        )
                    else:
                        delete_image_id.delete()
            return Response(
                {
                    "error_list": error_text,
                    "serializer_data": free_article_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_free_id):
        """자유게시판 특정 게시글 삭제"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        if request.user == free_article.author_id:
            free_article.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class CommentFreeView(APIView):
    def post(self, request, article_free_id):
        """자유게시판 댓글 작성"""
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_email_verified:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        serializer = FreeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author_id=request.user, article_free_id=free_article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_free_id, free_comment_id):
        """자유게시판 댓글 수정"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        free_comment = free_article.article_free_comment.get(id=free_comment_id)
        if request.user == free_comment.author_id:
            serializer = FreeCommentSerializer(free_comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_free_id, free_comment_id):
        """자유게시판 댓글 삭제"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        free_comment = free_article.article_free_comment.get(id=free_comment_id)
        if request.user == free_comment.author_id:
            free_comment.delete()
            return Response("댓글이 삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class ArticleFreeView(APIView):
    def get(self, request):
        """자유게시판 전체 게시글+이미지+댓글 조회"""
        page = request.GET.get("page", 1) if request.GET.get("page", 1) else 1
        free_article = ArticlesFree.objects.all()
        all_free_paginator = Paginator(free_article, 20)
        paginator_data = {
            "filtered_recipes_count": all_free_paginator.count,  # 검색된 레시피 개수
            "pages_num": all_free_paginator.num_pages,  # 총 페이지 수
        }
        if int(page) > all_free_paginator.num_pages:
            return Response("요청한 페이지가 없습니다.", status=status.HTTP_404_NOT_FOUND)
        page_obj = all_free_paginator.page(page)
        serializer = FreeArticleSerializer(page_obj, many=True)
        return Response(
            {"pagenation_data": paginator_data, "serializer_data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """자유게시판 게시글 작성"""
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_email_verified:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        serializer = FreeArticleSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(author_id=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ArticleFreeDetailView(APIView):
    def get(self, request, article_free_id):
        """자유게시판 특정 게시글+이미지+댓글 조회"""
        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        serializer = FreeArticleSerializer(free_article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, article_free_id):
        """자유게시판 특정 게시글+이미지 수정"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        if request.user == free_article.author_id:
            # 게시글 수정
            free_article_serializer = FreeArticleSerializer(
                free_article, data=request.data
            )
            if free_article_serializer.is_valid():
                free_article_serializer.save()
            else:
                return Response(
                    free_article_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )
            # 이미지 추가
            new_images = request.FILES
            if new_images:
                for image in new_images.getlist("image"):
                    ArticleFreeImages.objects.create(
                        article_free_id=free_article, free_image=image
                    )
            # 이미지 삭제
            delete_images = request.data.get("delete_image")
            error_text = []
            if delete_images:
                print(type(delete_images))
                delete_images = eval(delete_images)
                for delete_image in delete_images:
                    try:
                        delete_image_id = ArticleFreeImages.objects.get(
                            id=delete_image, article_free_id=free_article
                        )
                    except ObjectDoesNotExist:
                        error_text.append(
                            f"delete_image_error: db에서 [id:{delete_image}] 이미지 정보를 찾지 못했습니다."
                        )
                    else:
                        delete_image_id.delete()
            return Response(
                {
                    "error_list": error_text,
                    "serializer_data": free_article_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_free_id):
        """자유게시판 특정 게시글 삭제"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        if request.user == free_article.author_id:
            free_article.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class CommentFreeView(APIView):
    def post(self, request, article_free_id):
        """자유게시판 댓글 작성"""
        if not request.user.is_authenticated:
            return Response(
                {"message": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        if not request.user.is_email_verified:
            return Response(
                {"message": "이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN
            )

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        serializer = FreeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author_id=request.user, article_free_id=free_article)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_free_id, free_comment_id):
        """자유게시판 댓글 수정"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        free_comment = free_article.article_free_comment.get(id=free_comment_id)
        if request.user == free_comment.author_id:
            serializer = FreeCommentSerializer(free_comment, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_free_id, free_comment_id):
        """자유게시판 댓글 삭제"""
        if not request.user.is_authenticated:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)

        free_article = get_object_or_404(ArticlesFree, id=article_free_id)
        free_comment = free_article.article_free_comment.get(id=free_comment_id)
        if request.user == free_comment.author_id:
            free_comment.delete()
            return Response("댓글이 삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)



class YoutubeSummary(APIView):
    def __init__(self):
        super().__init__()
        openai_api_key = os.environ.get("OPENAI_API_KEY")

    def extract_youtube_video_id(self, url: str) -> str | None:
        found = re.search(r"(?:youtu\.be\/|watch\?v=)([\w-]+)", url)
        if found:
            return found.group(1)
        return None
    def get_video_transcript(self, video_id: str, language: str = "ko") -> str | None:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
            text = " ".join([line["text"] for line in transcript])
            return text
        except TranscriptsDisabled:
            return None



    def generate_summary(self, text: str) -> str:
        openai.api_key = os.getenv("OPENAI_API_KEY")

        instructions = "영상의 요리방법만 요약해주세요"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{instructions}\n\n{text[:1000]}",  # Truncate the prompt
            temperature=0.7,
            max_tokens=800,  # 글자수
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None
        )
        return response.choices[0].text.strip()

    def summarize_youtube_video(self, video_url: str) -> str:
        video_id = self.extract_youtube_video_id(video_url)

        if not video_id:
            return f"올바른 유튜브 url이 아닙니다. : {video_url}"

        # Try to retrieve the Korean transcript
        transcript = self.get_video_transcript(video_id, language="ko")

        if transcript is None:
            return f"한글 자막이 없는 영상입니다.: {video_url}"

        summary = self.generate_summary(transcript)
        return summary


    def post(self, request):
        video_url = request.data.get("url", "")
        if not video_url:
            return Response(
                {"message": "유튜브 url을 정확하게 입력해주세요"},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = self.summarize_youtube_video(video_url)
        # return Response({"summary": result}, status=status.HTTP_200_OK)
        if "올바른 유튜브 url이 아닙니다." in result or "한글 자막이 없는 영상입니다." in result:
            return Response({"message": result}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"summary": result}, status=status.HTTP_200_OK)