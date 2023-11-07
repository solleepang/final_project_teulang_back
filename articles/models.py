from django.db import models
from users.models import User


class ArticleRecipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )  # 회원 탈퇴시 author만 NULL로 되고 글은 유지됩니다.
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ingredients = models.TextField()
    star_avg = models.FloatField(null=True, blank=True)
    # 입력하지 않았을때 해당값은 False 입니다.
    api_recipe = models.BooleanField(default=False)
    article_recipe_img = models.ImageField(blank=True)
    bookmark_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.title)


class RecipeOrder(models.Model):
    article_recipe = models.ForeignKey(
        ArticleRecipe, on_delete=models.CASCADE, related_name="order_set"
    )
    content = models.TextField()
    recipe_img = models.ImageField(blank=True)
    order = models.IntegerField()

    def __str__(self):
        return str(self.article_recipe)


class StarRate(models.Model):
    star_rate = models.IntegerField(null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    article_recipe_id = models.ForeignKey(
        ArticleRecipe, on_delete=models.CASCADE, null=True)
