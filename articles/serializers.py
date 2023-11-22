from rest_framework import serializers

from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
    RecipeBookmark,
    CommentArticlesRecipe,
    ArticlesFree,
    ArticleFreeImages,
    CommentArticlesFree,
)
from users.serializers import UserDataSerializer
from users.models import User
import json
from django.db.models import Avg


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
    star_avg = serializers.SerializerMethodField()
    class Meta:
        model = StarRate
        fields = "__all__"

    def get_star_avg(self, obj):
        """ 해당 게시글 별점 평균 """
        star_rate = StarRate.objects.filter(
            article_recipe_id=obj.id).aggregate(Avg('star_rate'))
        return star_rate['star_rate__avg']


class RecipeBookmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeBookmark
        fields = "__all__"


class RecipeCommentSerializer(serializers.ModelSerializer):
    user_data = serializers.SerializerMethodField()
    article_recipe = serializers.SerializerMethodField()

    class Meta:
        model = CommentArticlesRecipe
        fields = "__all__"

    def get_user_data(self, obj):
        """ 해당 댓글 작성한 유저 데이터(이메일, 프로필, 닉네임, 팔로우)"""
        if obj.author:
            user = User.objects.get(id=obj.author.id)
            info = UserDataSerializer(user)
            return info.data
        else:
            return "탈퇴한 회원"

    def get_article_recipe(self, obj):
        return obj.article_recipe.id


class RecipeSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    user_data = serializers.SerializerMethodField()
    recipe_order = OrderSerializer(many=True)
    recipe_ingredients = IngredientSerializer(many=True)
    article_recipe_comment = RecipeCommentSerializer(many=True)
    star_avg = serializers.SerializerMethodField()
    bookmark_count = serializers.SerializerMethodField()

    def get_author(self, obj):
        if obj.author:
            return obj.author.nickname
        else:
            return "탈퇴한 회원"

    class Meta:
        model = ArticleRecipe
        fields = "__all__"

    def get_user_data(self, obj):
        """ 해당 게시글 작성한 유저 정보 : 이메일,프로필,닉네임,팔로우 """
        if obj.author:
            user = User.objects.get(id=obj.author.id)
            info = UserDataSerializer(user)
            return info.data
        else:
            return "탈퇴한 회원"

    def get_star_avg(self, obj):
        """ 해당 게시글 별점 평균 """
        star_rate = StarRate.objects.filter(
            article_recipe_id=obj.id).aggregate(Avg('star_rate'))
        return star_rate['star_rate__avg']

    def get_bookmark_count(self, obj):
        """ 해당 게시글을 북마크한 사람의 수 """
        bookmark = RecipeBookmark.objects.filter(
            article_recipe_id=obj.id).count()
        return bookmark


class FreeCommentSerializer(serializers.ModelSerializer):
    comment_user_data = serializers.SerializerMethodField()
    class Meta:
        model = CommentArticlesFree
        fields = "__all__"

    def get_comment_user_data(self, obj):
        """ 해당 댓글 작성한 유저 데이터(이메일, 프로필, 닉네임, 팔로우)"""
        if obj.author_id:
            user = User.objects.get(id=obj.author_id.id)
            info = UserDataSerializer(user)
            return info.data
        else:
            return "탈퇴한 회원"

class FreeImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleFreeImages
        fields = "__all__"

class FreeArticleSerializer(serializers.ModelSerializer):
    article_user_data = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    article_free_comment = FreeCommentSerializer(many=True, read_only=True)
    class Meta:
        model = ArticlesFree
        fields = "__all__"

    def create(self, validated_data):
        free_article = ArticlesFree.objects.create(**validated_data)
        images = self.context['request'].FILES
        for image in images.getlist('image'):
            ArticleFreeImages.objects.create(article_free_id=free_article, free_image=image)
        return free_article
    
    def get_article_user_data(self, obj):
        """ 해당 댓글 작성한 유저 데이터(이메일, 프로필, 닉네임, 팔로우)"""
        if obj.author_id:
            user = User.objects.get(id=obj.author_id.id)
            info = UserDataSerializer(user)
            return info.data
        else:
            return "탈퇴한 회원"
        
    def get_images(self, obj):
        images = ArticleFreeImages.objects.filter(article_free_id=obj)
        if images:
            return FreeImagesSerializer(images, many=True).data
        else:
            return        
    
        