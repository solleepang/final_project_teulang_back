from rest_framework import serializers

from articles.models import ArticleRecipe, RecipeOrder, StarRate


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


class StarRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StarRate
        fields = "__all__"
