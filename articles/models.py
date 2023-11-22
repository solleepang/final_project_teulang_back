from django.db import models
from users.models import User


class ArticleRecipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="articles_recipe"
    )  # 회원 탈퇴시 author만 NULL로 되고 글은 유지됩니다.
    title = models.CharField(max_length=50)
    description = models.CharField(
        max_length=255, null=True, blank=True
    )  # 레시피 간단 설명 추가됨
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # 입력하지 않았을때 해당값은 False 입니다.
    api_recipe = models.BooleanField(default=False)
    recipe_thumbnail = models.ImageField(
        blank=True, upload_to="article/recipe_thumbnail", default="recipe_defalt.jpg"
    )  # thumbnail로 이름 변경
    recipe_thumbnail_api = models.CharField(
        max_length=1000, null=True, blank=True, default=""
    )  # 프론트에서 이미지 URL로 보여주기 위해 모델필드 추가

    def __str__(self):
        return str(self.title)


class RecipeOrder(models.Model):
    article_recipe = models.ForeignKey(
        ArticleRecipe,
        on_delete=models.CASCADE,
        related_name="recipe_order",  # order_set -> recipe_order
    )
    content = models.TextField()
    recipe_img = models.ImageField(
        null=True,
        blank=True,
        upload_to="article/recipe_order_img",
    )
    order = models.IntegerField()
    recipe_img_api = models.CharField(
        max_length=1000, null=True, blank=True, default=""
    )  # 프론트에서 이미지 URL로 보여주기 위해 모델필드 추가

    def __str__(self):
        return str(self.article_recipe)


class ArticleRecipeIngredients(models.Model):
    article_recipe = models.ForeignKey(
        ArticleRecipe,
        on_delete=models.CASCADE,
        related_name="recipe_ingredients",
    )
    ingredients = models.CharField(max_length=255)

    def __str__(self):
        return str(self.article_recipe)


class StarRate(models.Model):
    star_rate = models.IntegerField()
    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recipe_star_rate"
    )
    article_recipe_id = models.ForeignKey(
        ArticleRecipe,
        on_delete=models.CASCADE,
        null=True,
        related_name="recipe_star_rate",
    )


class RecipeBookmark(models.Model):
    article_recipe_id = models.ForeignKey(
        ArticleRecipe,
        on_delete=models.CASCADE,
        null=True,
        related_name="recipe_bookmark",
    )
    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recipe_bookmark"
    )


class CommentArticlesRecipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="user_comment"
    )
    article_recipe = models.ForeignKey(  # ERD 설계에 맞춰서 필드명 수정
        ArticleRecipe, on_delete=models.CASCADE, related_name="article_recipe_comment"
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ArticlesFree(models.Model):
    FREE_ARTICLE_CATEGORY = [
        ('review', 'Review'),
        ('chat', 'Chat')
    ]
    author_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="articles_free")
    title = models.CharField(max_length=50)
    content = models.TextField(null=True, blank=True)
    category = models.CharField(max_length=25, choices=FREE_ARTICLE_CATEGORY, default='chat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.title)
    

class ArticleFreeImages(models.Model):
    article_free_id = models.ForeignKey(ArticlesFree, on_delete=models.CASCADE, related_name="article_free_image", null=True)
    free_image = models.ImageField(blank=True, upload_to="article/free_image")


class CommentArticlesFree(models.Model):
    author_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_comment_free")
    article_free_id = models.ForeignKey(ArticlesFree, on_delete=models.CASCADE, related_name="article_free_comment", null=True)
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)