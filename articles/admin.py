from django.contrib import admin
from articles.models import (
    ArticleRecipe,
    RecipeOrder,
    ArticleRecipeIngredients,
    StarRate,
)

admin.site.register(ArticleRecipe)
admin.site.register(RecipeOrder)
admin.site.register(ArticleRecipeIngredients)
admin.site.register(StarRate)
