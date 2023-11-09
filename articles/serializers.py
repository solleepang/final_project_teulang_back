from rest_framework import serializers

from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
    RecipeBookmark,
    CommentArticlesRecipe,
)
from users.serializers import UserDataSerializer
from users.models import User
import json


class RecipeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipe
        fields = (
            "title",
            "recipe_thumbnail",
            "description",
            "api_recipe",
        )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeOrder
        fields = "__all__"


class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeOrder
        fields = ("order", "recipe_img", "content")


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipeIngredients
        fields = "__all__"


class IngredientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleRecipeIngredients
        fields = ("ingredients",)


class StarRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarRate
        fields = "__all__"


class RecipeBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeBookmark
        fields = "__all__"


class RecipeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentArticlesRecipe
        fields = ("content",)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    user_data = serializers.SerializerMethodField()
    recipe_order = OrderSerializer(many=True)
    recipe_ingredients = IngredientSerializer(many=True)
    article_recipe_comment = RecipeCommentSerializer(many=True)
    star_avg = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.nickname

    class Meta:
        model = ArticleRecipe
        fields = "__all__"

    def get_user_data(self, obj):
        """ 해당 게시글 작성한 유저 정보 : 이메일,프로필,닉네임,팔로우 """
        user = User.objects.get(id=obj.author.id)
        info = UserDataSerializer(user)
        return info.data

    def get_star_avg(self, obj):
        """ 해당 게시글 별점 평균 """
        star_rate = StarRate.objects.filter(article_recipe_id=obj.id)
        if len(star_rate) < 1:
            star_avg = 0
        else:
            star_avg = sum([star_rate[i].star_rate for i in range(
                len(star_rate))])/len(star_rate)
        return star_avg

    def get_bookmark_count(self, obj):
        """ 해당 게시글을 북마크한 사람의 수 """
        bookmark = RecipeBookmark.objects.filter(article_recipe_id=obj.id)
        return len(bookmark)
