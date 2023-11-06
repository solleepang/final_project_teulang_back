from django.urls import path
from articles import views

urlpatterns = [
    path('recipe/<int:article_recipe_id>/comment/', views.CommentView.as_view()),
    path('recipe/<int:article_recipe_id>/comment/<int:recipe_comment_id>',
         views.CommentView.as_view()),
]
