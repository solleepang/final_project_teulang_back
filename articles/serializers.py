from rest_framework import serializers

from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
    RecipeBookmark,
    CommentArticlesRecipe,
)


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    def get_author(self, obj):
        return obj.author.nickname

    class Meta:
        model = ArticleRecipe
        fields = "__all__"


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
