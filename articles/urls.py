from django.urls import path
from articles import views, youtube

urlpatterns = [
    path("recipe/", views.RecipeView.as_view(), name="recipe_view"),
    path(
        "recipe/<int:article_recipe_id>/",
        views.RecipeDetailView.as_view(),
        name="recipe_detail_view",
    ),
    # path(
    #     "recipe/<int:article_recipe_id>/order/",
    #     views.OrderView.as_view(),
    #     name="order_view",
    # ),
    # path(
    #     "recipe/<int:article_recipe_id>/order/<int:recipe_order_id>/",
    #     views.OrderDetailView.as_view(),
    #     name="order_detail_view",
    # ),
    # path(
    #     "recipe/<int:article_recipe_id>/ingredients/",
    #     views.IngredientView.as_view(),
    #     name="order_view",
    # ),
    # path(
    #     "recipe/<int:article_recipe_id>/ingredients/<int:article_recipe_ingredients_id>/",
    #     views.IngredientDetailView.as_view(),
    #     name="order_detail_view",
    # ),
    path(
        "recipe/<int:article_recipe_id>/star_rate/",
        views.StarRateView.as_view(),
        name="star_rate_view",
    ),
    path(
        "recipe/<int:article_recipe_id>/bookmark/",
        views.RecipeBookmarkView.as_view(),
        name="bookmark_view",
    ),
    path("recipe/<int:article_recipe_id>/comment/", views.CommentView.as_view()),
    path(
        "recipe/<int:article_recipe_id>/comment/<int:recipe_comment_id>/",
        views.CommentView.as_view(),
    ),
    path(
        "recipe/search",
        views.RecipeSearchView.as_view(),
        name="recipe_search_view",
    ),
    path(
        "fetch-and-save-data/<int:start>/<int:end>/",
        views.fetch_and_save_openapi_data,
        name="fetch_and_save_openapi_data",
    ),
    path(
        "recipe/bookmark/",
        views.RecipeUserBookmarkView.as_view(),
        name="user_bookmark_view",
    ),
    path(
        "free/",
        views.ArticleFreeView.as_view(),
        name="free_view",
    ),
    path(
        "free/<int:article_free_id>/",
        views.ArticleFreeDetailView.as_view(),
        name="free_detail_view",
    ),
    path(
        "free/<int:article_free_id>/comment/",
        views.CommentFreeView.as_view(),
        name="free_comment_view",
    ),
    path(
        "free/<int:article_free_id>/comment/<int:free_comment_id>/",
        views.CommentFreeView.as_view(),
        name="free_comment_view",
    ),
    path(
        "detect_objects/",
        views.DetectObjectsAPI.as_view(),
        name="detect_objects_api",
    ),
    path(
        "youtube/",
        youtube.YoutubeSummary.as_view(),
        name="youtube_summary",
    ),
]
