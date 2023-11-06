from django.db import models
from users.models import User


class RecipeComment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='user_comment')
    recipe = models.ForeignKey(
        ArticleRecipe, on_delete=models.CASCADE, related_name='article_recipe_comment')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
