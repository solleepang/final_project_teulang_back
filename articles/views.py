import requests
from django.http import JsonResponse
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
    RecipeBookmark,
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
)
from users.models import User
from django.core.exceptions import ObjectDoesNotExist
import json
from teulang.settings import env


class RecipeView(APIView):
    # 레시피 전체 불러오기
    def get(self, request):
        recipes = ArticleRecipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 레시피, 재료, 순서 생성
    def post(self, request):
        # 레시피 작성 권한 설정(로그인, 이메일 인증)
        if not request.user.is_authenticated:
            return Response({"message":"로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.is_email_verified == False:
            return Response({"message":"이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN)
        # 레시피 저장
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            recipe = serializer.save(author=request.user)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # 재료 저장
        ingredients = request.data["recipe_ingredients"].split(",")
        for ingredient in ingredients:
            ingredient_data = {"ingredients": ingredient}
            serializer_ingredients = IngredientCreateSerializer(
                data=ingredient_data)
            if serializer_ingredients.is_valid():
                serializer_ingredients.save(article_recipe_id=recipe.id)
            else:
                return Response("재료를 확인해주세요.", status=status.HTTP_400_BAD_REQUEST)
        # 조리 순서와 이미지 저장
        orders = eval(request.data["recipe_order"])
        for i in range(1, len(orders)+1):
            # 조리 순서 이미지 없으면 null, request body에 조리 순서 이미지의 키값 없으면 null
            recipe_img = request.data.get(
                f'{i}') if request.data.get(f'{i}') else None
            order_image_data = {
                "order": i,
                "content": orders[i-1]["content"],
                "recipe_img": recipe_img,
            }
            order_image_serializer = OrderCreateSerializer(
                data=order_image_data)
            if order_image_serializer.is_valid():
                order_image_serializer.save(article_recipe_id=recipe.id)
            else:
                return Response("순서를 확인해주세요.", status=status.HTTP_400_BAD_REQUEST)
        final_serializer = RecipeSerializer(recipe)
        return Response(final_serializer.data, status=status.HTTP_200_OK)


class RecipeDetailView(APIView):
    # 상세 레시피 불러오기
    def get(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 레시피 수정하기
    def put(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:
            serializer = RecipeCreateSerializer(recipe, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    # 레시피 삭제하기
    def delete(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:
            recipe.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class OrderView(APIView):
    # 각 레시피의 조리 순서 전부 가져오기
    def get(self, request, article_recipe_id):
        recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        recipe_orders = recipe.recipe_order.all()  # order_set -> recipe_order
        serializer = OrderSerializer(recipe_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrderDetailView(APIView):
    # 각 레시피의 조리순서 수정하기 (하나씩 각각)
    def put(self, request, article_recipe_id, recipe_order_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        # recipe_order = get_object_or_404(RecipeOrder, id=recipe_order_id) ==> 식재료와 마찬가지로 오류 수정
        recipe_order = recipe.recipe_order.get(
            id=recipe_order_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 수정 안되게 설정
            serializer = OrderCreateSerializer(recipe_order, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    # 각 레시피의 조리순서 삭제하기 (하나씩 각각)
    def delete(self, request, article_recipe_id, recipe_order_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        recipe_order = recipe.recipe_order.get(
            id=recipe_order_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
            recipe_order.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class IngredientView(APIView):
    # 각 레시피의 재료 전부 가져오기
    def get(self, request, article_recipe_id):
        recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        recipe_ingredients = recipe.recipe_ingredients.all()
        serializer = IngredientSerializer(recipe_ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class IngredientDetailView(APIView):
    # 각 레시피의 재료 수정하기 (하나씩 각각)
    def put(self, request, article_recipe_id, article_recipe_ingredients_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        # url에서 받아온 recipe_id값과 동일한 recipe 내에서 역참조한 식재료 목록 중 ingredients_id와 같은 값을 갖는 식재료 목록을 하나씩 가져옵니다.
        recipe_ingredients = recipe.recipe_ingredients.get(
            id=article_recipe_ingredients_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 수정 안되게 설정
            serializer = IngredientCreateSerializer(
                recipe_ingredients, data=request.data
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    # 각 레시피의 재료 삭제하기 (하나씩 각각)
    def delete(self, request, article_recipe_id, article_recipe_ingredients_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        recipe_ingredients = recipe.recipe_ingredients.get(
            id=article_recipe_ingredients_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
            recipe_ingredients.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class StarRateView(APIView):
    def post(self, request, article_recipe_id):
        """요청 유저 아이디로 해당 레시피에 별점 추가"""
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
            StarRate.objects.get(
                user_id=user, article_recipe_id=article_recipe_id)
        except ObjectDoesNotExist:
            # 별점이 존재하지 않으면 새로 추가
            serializer = StarRateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user_id=user, article_recipe_id=recipe)
                return Response("별점이 추가되었습니다.", status=status.HTTP_201_CREATED)
            else:
                return Response("잘못된 요청입니다.", status=status.HTTP_400_BAD_REQUEST)
        else:
            # 별점 중복 확인
            return Response("이미 작성한 별점이 있습니다.", status=status.HTTP_409_CONFLICT)


class RecipeBookmarkView(APIView):
    """요청 유저 아이디로 해당 레시피를 북마크 추가"""

    def post(self, request, article_recipe_id):
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
            return Response({"message":"로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED)
        if request.user.is_email_verified == False:
            return Response({"message":"이메일 인증이 필요합니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = RecipeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user,
                            article_recipe_id=article_recipe_id)
            return Response("댓글이 작성되었습니다", status=status.HTTP_201_CREATED)
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
                return Response("댓글이 수정되었습니다", status=status.HTTP_200_OK)
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
        """검색된 재료 포함하는 레시피 구한 후 object 반환"""
        quart_string = request.GET["q"]
        ingredients = quart_string.split(",")
        recipes = []
        for i in range(len(ingredients)):
            if i < 1:
                recipes = ArticleRecipe.objects.filter(
                    recipe_ingredients__ingredients__contains=ingredients[i].strip(
                    )
                )
            else:
                recipes = recipes.filter(
                    recipe_ingredients__ingredients__contains=ingredients[i].strip(
                    )
                )
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


def fetch_and_save_openapi_data(request):
    # api키 받기
    api_key = env("API_KEY")

    # API URL 입력 (맨뒤 1124 입력후 urls.py의 경로로 get 요청시 레시피를 가져옵니다.)
    url = f"http://openapi.foodsafetykorea.go.kr/api/{api_key}/COOKRCP01/json/1000/1010"
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
                recipe_thumbnail=recipe_data["ATT_FILE_NO_MK"],
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
                        recipe_img=img_url,
                        order=i,
                    )

        return JsonResponse({"message": "데이터 가져오기 및 저장 완료"})
    else:
        return JsonResponse({"error": "데이터 가져오기 실패"}, status=500)
