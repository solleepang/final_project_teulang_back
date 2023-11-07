from django.urls import path
from articles import views

urlpatterns = [
    path("recipe/", views.RecipeView.as_view(), name="recipe_view"),
    path(
        "recipe/<int:article_recipe_id>/",
        views.RecipeDetailView.as_view(),
        name="recipe_detail_view",
    ),
    path(
        "recipe/<int:article_recipe_id>/order/",
        views.OrderView.as_view(),
        name="order_view",
    ),
    path(
        "recipe/<int:article_recipe_id>/order/<int:recipe_order_id>/",
        views.OrderDetailView.as_view(),
        name="order_detail_view",
    ),
    path("recipe/<int:article_recipe_id>/star_rate/",
         views.StarRateView.as_view(), name="star_rate_view"),
]
