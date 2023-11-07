from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from articles.models import ArticleRecipe, RecipeOrder
from articles.serializers import (
    RecipeSerializer,
    RecipeCreateSerializer,
    OrderSerializer,
    OrderCreateSerializer,
    RecipeCommentSerializer,
)
from users.models import User


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


class CommentView(APIView):

    def get(self, request, article_recipe_id):
        """ 특정 recipe의 댓글 조회 """
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comments = recipe.article_recipe_comment.all()
        serializer = RecipeCommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, article_recipe_id):
        """ 댓글 작성 """
        serializer = RecipeCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, recipe_id=article_recipe_id)
            return Response("댓글이 작성되었습니다", status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, article_recipe_id, recipe_comment_id):
        """ 댓글 수정 """
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comment = recipe.article_recipe_comment.get(id=recipe_comment_id)
        serializer = RecipeCommentSerializer(comment, data=request.data)
        if request.user == comment.author:
            if serializer.is_valid():
                serializer.save()
                return Response("댓글이 수정되었습니다", status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.is_authenticated == False:    # request.user.is_anonymous == True를 지금과 같은 형태로 변경
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)
        elif request.user != comment.author:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, article_recipe_id, recipe_comment_id):
        """ 댓글 삭제 """
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        comment = recipe.article_recipe_comment.get(id=recipe_comment_id)
        if request.user == comment.author:
            comment.delete()
            return Response("댓글이 삭제되었습니다", status=status.HTTP_204_NO_CONTENT)
        elif request.user.is_authenticated == False:
            return Response("로그인 정보가 없습니다", status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)
