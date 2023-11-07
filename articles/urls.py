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
    path('recipe/<int:article_recipe_id>/comment/', views.CommentView.as_view()),
    path('recipe/<int:article_recipe_id>/comment/<int:recipe_comment_id>',
         views.CommentView.as_view()),
]
