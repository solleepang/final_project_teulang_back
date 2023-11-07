from django.contrib import admin
from articles.models import ArticleRecipe, RecipeOrder, StarRate

admin.site.register(ArticleRecipe)
admin.site.register(RecipeOrder)
admin.site.register(StarRate)
