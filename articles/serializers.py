from rest_framework import serializers

from articles.models import ArticleRecipe, RecipeOrder, CommentArticlesRecipe


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
            "ingredients",
            "article_recipe_img",
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


class RecipeCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentArticlesRecipe
        fields = ("content",)
