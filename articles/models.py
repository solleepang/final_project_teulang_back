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
        blank=True, upload_to='article/recipe_thumbnail', default='recipe_defalt.jpg')  # thumbnail로 이름 변경

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
        null=True, blank=True, upload_to='article/recipe_order_img', )
    order = models.IntegerField()

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
    star_rate = models.IntegerField(null=True, blank=True)
    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recipe_star_rate")
    article_recipe_id = models.ForeignKey(
        ArticleRecipe, on_delete=models.CASCADE, null=True, related_name="recipe_star_rate"
    )


class RecipeBookmark(models.Model):
    article_recipe_id = models.ForeignKey(
        ArticleRecipe, on_delete=models.CASCADE, null=True, related_name="recipe_bookmark"
    )
    user_id = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="recipe_bookmark")


class CommentArticlesRecipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='user_comment')
    article_recipe = models.ForeignKey(         # ERD 설계에 맞춰서 필드명 수정
        ArticleRecipe, on_delete=models.CASCADE, related_name='article_recipe_comment')
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
