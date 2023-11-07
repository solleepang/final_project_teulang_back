from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articles.models import ArticleRecipe, RecipeOrder, StarRate
from articles.serializers import (
    RecipeSerializer,
    RecipeCreateSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    StarRateSerializer,
)
from users.models import User
from django.core.exceptions import ObjectDoesNotExist


class RecipeView(APIView):
    # 레시피 전체 불러오기
    def get(self, request):
        recipes = ArticleRecipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 레시피 작성하기(몸통부분)
    def post(self, request):
        serializer = RecipeCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        recipe_orders = recipe.order_set.all()
        serializer = OrderSerializer(recipe_orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 각 레시피의 조리순서 작성하기
    def post(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 작성 안되게 설정
            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(article_recipe_id=article_recipe_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class OrderDetailView(APIView):
    # 각 레시피의 조리순서 수정하기 (하나씩 각각)
    def put(self, request, article_recipe_id, recipe_order_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        recipe_order = get_object_or_404(RecipeOrder, id=recipe_order_id)
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
        recipe_order = get_object_or_404(RecipeOrder, id=recipe_order_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
            recipe_order.delete()
            return Response("삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class StarRateView(APIView):
    def post(self, request, article_recipe_id):
        """ 요청 유저 아이디로 해당 레시피에 별점 추가 """
        # 로그인 정보 확인
        try:
            user = User.objects.get(id=request.user.id)
        except ObjectDoesNotExist:
            return Response("로그인 정보가 없습니다.", status=status.HTTP_401_UNAUTHORIZED)
        # 요청한 레시피 있는지 확인
        try:
            recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        except ObjectDoesNotExist:
            return Response("존재하지 않는 레시피입니다.", status=status.HTTP_401_UNAUTHORIZED)
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
