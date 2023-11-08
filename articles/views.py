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
        recipe_orders = recipe.recipe_order.all()  # order_set -> recipe_order
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


class IngredientView(APIView):
    # 각 레시피의 재료 전부 가져오기
    def get(self, request, article_recipe_id):
        recipe = ArticleRecipe.objects.get(id=article_recipe_id)
        recipe_ingredients = recipe.recipe_ingredients.all()
        serializer = IngredientSerializer(recipe_ingredients, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 각 레시피의 재료 작성하기
    def post(self, request, article_recipe_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 작성 안되게 설정
            serializer = IngredientCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(article_recipe_id=article_recipe_id)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다", status=status.HTTP_403_FORBIDDEN)


class IngredientDetailView(APIView):
    # 각 레시피의 재료 수정하기 (하나씩 각각)
    def put(self, request, article_recipe_id, article_recipe_ingredients_id):
        recipe = get_object_or_404(ArticleRecipe, id=article_recipe_id)
        # recipe_ingredients = get_object_or_404(
        #     ArticleRecipeIngredients, id=article_recipe_ingredients_id
        # )
        recipe_ingredients = recipe.recipe_ingredients.get(
            id=article_recipe_ingredients_id)
        print(recipe_ingredients.ingredients)
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
        recipe_ingredients = get_object_or_404(
            ArticleRecipeIngredients, id=article_recipe_ingredients_id
        )
        if request.user == recipe.author:  # 해당 레시피 작성자가 아니면 삭제 안되게 설정
            recipe_ingredients.delete()
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
            return Response("존재하지 않는 레시피입니다.", status=status.HTTP_400_BAD_REQUEST)
        # 본인의 글인지 확인
        if recipe.author == request.user:
            return Response("자신의 글에는 별점을 매길 수 없습니다.", status=status.HTTP_403_FORBIDDEN)

        try:
            RecipeBookmark.objects.get(
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
    """ 요청 유저 아이디로 해당 레시피를 북마크 추가 """

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
                user_id=user, article_recipe_id=article_recipe_id)
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
